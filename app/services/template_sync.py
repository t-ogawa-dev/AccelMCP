"""
Template Synchronization Service

GitHubリポジトリからテンプレートデータを取得し、DBに同期するサービス
"""
import os
import json
import logging
import requests
import yaml
from datetime import datetime
from packaging import version as version_parser
from flask import current_app
from app import __version__ as ACCEL_MCP_VERSION
from app.models.models import db, McpServiceTemplate, McpCapabilityTemplate, AdminSettings

logger = logging.getLogger(__name__)


class TemplateNotFoundError(Exception):
    """テンプレートが見つからない場合のエラー"""
    pass


class VersionIncompatibleError(Exception):
    """バージョン非互換エラー"""
    pass


class TemplateSyncService:
    """テンプレート同期サービス"""
    
    def __init__(self):
        self.base_url = current_app.config.get('TEMPLATE_REPOSITORY_URL')
        self.index_file = current_app.config.get('TEMPLATE_INDEX_FILE', 'index.yaml')
        self.versions_dir = current_app.config.get('TEMPLATE_VERSIONS_DIR', 'versions')
    
    def get_index_url(self):
        """index.yamlのURLを取得"""
        return f"{self.base_url}/{self.index_file}"
    
    def get_template_url(self, filename):
        """テンプレートファイルのURLを取得"""
        return f"{self.base_url}/{self.versions_dir}/{filename}"
    
    def fetch_yaml(self, url):
        """YAMLファイルをHTTP経由で取得"""
        try:
            logger.info(f"Fetching YAML from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return yaml.safe_load(response.text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch YAML from {url}: {e}")
            raise TemplateNotFoundError(f"Failed to fetch template: {e}")
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise TemplateNotFoundError(f"Invalid YAML format: {e}")
    
    def check_for_updates(self):
        """
        更新チェック
        
        Returns:
            dict: {
                'has_update': bool,
                'current_version': str,
                'latest_version': str,
                'changelog': str,
                'template_count': int
            }
        """
        try:
            # index.yamlを取得
            index_data = self.fetch_yaml(self.get_index_url())
            
            # 現在のAccelMCPバージョンと互換性のある最新バージョンを探す
            compatible_version = self._find_compatible_version(index_data['versions'])
            
            if not compatible_version:
                raise VersionIncompatibleError(
                    f"No compatible template version found for AccelMCP {ACCEL_MCP_VERSION}"
                )
            
            # 現在インストールされているバージョンを取得
            current_version = self._get_current_template_version()
            
            # バージョン比較
            has_update = False
            if current_version:
                has_update = version_parser.parse(compatible_version['version']) > version_parser.parse(current_version)
            else:
                # 未インストールの場合は常に更新あり
                has_update = True
            
            return {
                'has_update': has_update,
                'current_version': current_version or 'None',
                'latest_version': compatible_version['version'],
                'changelog': compatible_version.get('changelog', ''),
                'template_count': compatible_version.get('template_count', 0),
                'released_at': compatible_version.get('released_at', ''),
                'schema_breaking': compatible_version.get('schema_breaking', False)
            }
            
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            raise
    
    def sync_templates(self):
        """
        テンプレートを同期
        
        Returns:
            dict: {
                'success': bool,
                'version': str,
                'added': int,
                'updated': int,
                'message': str
            }
        """
        try:
            # 更新チェック
            update_info = self.check_for_updates()
            
            if not update_info['has_update']:
                return {
                    'success': True,
                    'version': update_info['current_version'],
                    'added': 0,
                    'updated': 0,
                    'message': 'Already up to date'
                }
            
            # index.yamlを取得
            index_data = self.fetch_yaml(self.get_index_url())
            compatible_version = self._find_compatible_version(index_data['versions'])
            
            # テンプレートファイルを取得
            template_url = self.get_template_url(compatible_version['file'])
            template_data = self.fetch_yaml(template_url)
            
            # DBに同期
            stats = self._sync_to_database(template_data)
            
            # バージョン情報を保存
            self._save_template_version(template_data['version'])
            
            logger.info(f"Template sync completed: {stats}")
            
            return {
                'success': True,
                'version': template_data['version'],
                'added': stats['added'],
                'updated': stats['updated'],
                'message': f"Successfully synced {stats['added'] + stats['updated']} templates"
            }
            
        except Exception as e:
            logger.error(f"Template sync failed: {e}")
            db.session.rollback()
            raise
    
    def _find_compatible_version(self, versions):
        """
        現在のAccelMCPバージョンと互換性のある最新バージョンを探す
        
        Args:
            versions: バージョンリスト
            
        Returns:
            dict: 互換性のあるバージョン情報
        """
        current_version = version_parser.parse(ACCEL_MCP_VERSION)
        compatible_versions = []
        
        for ver in versions:
            min_ver = version_parser.parse(ver['accel_mcp_min'])
            max_ver = version_parser.parse(ver['accel_mcp_max']) if ver.get('accel_mcp_max') else None
            
            # バージョン範囲チェック
            if current_version >= min_ver:
                if max_ver is None or current_version <= max_ver:
                    compatible_versions.append(ver)
        
        if not compatible_versions:
            return None
        
        # 最新バージョンを返す
        compatible_versions.sort(key=lambda x: version_parser.parse(x['version']), reverse=True)
        return compatible_versions[0]
    
    def _get_current_template_version(self):
        """現在インストールされているテンプレートバージョンを取得"""
        setting = AdminSettings.query.filter_by(setting_key='builtin_templates_version').first()
        return setting.setting_value if setting else None
    
    def _save_template_version(self, template_version):
        """テンプレートバージョンを保存"""
        setting = AdminSettings.query.filter_by(setting_key='builtin_templates_version').first()
        if setting:
            setting.setting_value = template_version
            setting.updated_at = datetime.utcnow()
        else:
            setting = AdminSettings(
                setting_key='builtin_templates_version',
                setting_value=template_version
            )
            db.session.add(setting)
        
        # 最終更新日時も保存
        last_check = AdminSettings.query.filter_by(setting_key='last_template_sync').first()
        if last_check:
            last_check.setting_value = datetime.utcnow().isoformat()
            last_check.updated_at = datetime.utcnow()
        else:
            last_check = AdminSettings(
                setting_key='last_template_sync',
                setting_value=datetime.utcnow().isoformat()
            )
            db.session.add(last_check)
        
        db.session.commit()
    
    def _sync_to_database(self, template_data):
        """
        テンプレートデータをデータベースに同期
        
        Args:
            template_data: YAMLから読み込んだテンプレートデータ
            
        Returns:
            dict: {'added': int, 'updated': int}
        """
        added = 0
        updated = 0
        template_version = template_data['version']
        
        for tpl in template_data['templates']:
            template_id = tpl['id']
            
            # 既存テンプレートを検索（template_idで）
            existing = McpServiceTemplate.query.filter_by(
                template_id=template_id,
                template_type='builtin'
            ).first()
            
            if existing:
                # 更新
                logger.info(f"Updating template: {tpl['name']} ({template_id})")
                existing.name = tpl['name']
                existing.service_type = tpl['service_type']
                existing.mcp_url = tpl.get('mcp_url')
                existing.official_url = tpl.get('official_url')
                existing.description = tpl['description']
                existing.common_headers = json.dumps(tpl.get('common_headers', {}))
                existing.icon = tpl.get('icon')
                existing.category = tpl.get('category')
                existing.template_version = template_version
                existing.updated_at = datetime.utcnow()
                
                # 既存のcapabilityを削除
                McpCapabilityTemplate.query.filter_by(template_id=existing.id).delete()
                
                template = existing
                updated += 1
            else:
                # 新規作成
                logger.info(f"Adding new template: {tpl['name']} ({template_id})")
                template = McpServiceTemplate(
                    name=tpl['name'],
                    template_type='builtin',
                    service_type=tpl['service_type'],
                    mcp_url=tpl.get('mcp_url'),
                    official_url=tpl.get('official_url'),
                    description=tpl['description'],
                    common_headers=json.dumps(tpl.get('common_headers', {})),
                    icon=tpl.get('icon'),
                    category=tpl.get('category'),
                    template_id=template_id,
                    template_version=template_version
                )
                db.session.add(template)
                db.session.flush()
                added += 1
            
            # Capabilityを追加（APIタイプの場合）
            if tpl['service_type'] == 'api' and 'capabilities' in tpl:
                for cap in tpl['capabilities']:
                    capability = McpCapabilityTemplate(
                        template_id=template.id,
                        name=cap['name'],
                        capability_type=cap['capability_type'],
                        endpoint_path=cap.get('endpoint_path', ''),
                        method=cap.get('method', 'GET'),
                        description=cap.get('description', ''),
                        headers=json.dumps(cap.get('headers', {})),
                        body_params=json.dumps(cap.get('body_params', {})),
                        query_params=json.dumps(cap.get('query_params', {}))
                    )
                    db.session.add(capability)
        
        db.session.commit()
        
        return {'added': added, 'updated': updated}
