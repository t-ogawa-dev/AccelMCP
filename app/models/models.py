"""
Database models for MCP Server
"""
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ConnectionAccount(db.Model):
    """接続アカウント - MCPサービスに接続するためのアカウント"""
    __tablename__ = 'connection_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bearer_token = db.Column(db.String(100), unique=True, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('AccountPermission', back_populates='account', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bearer_token': self.bearer_token,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class McpService(db.Model):
    """MCPサービス - 複数のアプリを束ねる上位概念"""
    __tablename__ = 'mcp_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    access_control = db.Column(db.String(20), nullable=False, default='restricted')  # 'public' or 'restricted'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    apps = db.relationship('Service', back_populates='mcp_service', cascade='all, delete-orphan')
    permissions = db.relationship('AccountPermission', back_populates='mcp_service', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'description': self.description,
            'access_control': self.access_control,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'apps_count': len(self.apps) if self.apps else 0
        }


class Service(db.Model):
    __tablename__ = 'apps'
    
    id = db.Column(db.Integer, primary_key=True)
    mcp_service_id = db.Column(db.Integer, db.ForeignKey('mcp_services.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(20), nullable=False)  # 'api' or 'mcp'
    mcp_url = db.Column(db.String(500))  # MCP接続先URL (service_type='mcp'の場合)
    common_headers = db.Column(db.Text)  # JSON string
    description = db.Column(db.Text)
    access_control = db.Column(db.String(20), nullable=False, default='public')  # 'public' or 'restricted'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)  # 有効/無効フラグ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mcp_service = db.relationship('McpService', back_populates='apps')
    capabilities = db.relationship('Capability', back_populates='service', cascade='all, delete-orphan')
    permissions = db.relationship('AccountPermission', back_populates='app', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'mcp_service_id': self.mcp_service_id,
            'name': self.name,
            'service_type': self.service_type,
            'mcp_url': self.mcp_url,
            'common_headers': json.loads(self.common_headers) if self.common_headers else {},
            'description': self.description,
            'access_control': self.access_control,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Capability(db.Model):
    __tablename__ = 'capabilities'
    __table_args__ = (
        db.UniqueConstraint('app_id', 'name', name='uq_capability_app_name'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    capability_type = db.Column(db.String(50), nullable=False)  # 'tool', 'resource', 'prompt' (API), or 'mcp_tool' (MCP)
    url = db.Column(db.String(500))  # endpoint (for tool/resource)
    headers = db.Column(db.Text)  # JSON string (for tool)
    body_params = db.Column(db.Text)  # JSON string (for tool)
    template_content = db.Column(db.Text)  # prompt template (for prompt)
    description = db.Column(db.Text)
    access_control = db.Column(db.String(20), nullable=False, default='public')  # 'public' or 'restricted'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)  # 有効/無効フラグ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service = db.relationship('Service', back_populates='capabilities')
    permissions = db.relationship('AccountPermission', back_populates='capability', cascade='all, delete-orphan')
    
    def to_dict(self):
        result = {
            'id': self.id,
            'app_id': self.app_id,
            'service_id': self.app_id,  # Alias for compatibility
            'name': self.name,
            'capability_type': self.capability_type,
            'url': self.url,
            'headers': json.loads(self.headers) if self.headers else {},
            'body_params': json.loads(self.body_params) if self.body_params else {},
            'template_content': self.template_content,
            'description': self.description,
            'access_control': self.access_control,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        # Include mcp_service_id from parent service
        if self.service and self.service.mcp_service_id:
            result['mcp_service_id'] = self.service.mcp_service_id
        return result


class AccountPermission(db.Model):
    """接続アカウントの権限管理 - 3階層サポート"""
    __tablename__ = 'account_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('connection_accounts.id'), nullable=False)
    
    # 3-tier permission: exactly one of these must be set
    mcp_service_id = db.Column(db.Integer, db.ForeignKey('mcp_services.id'), nullable=True)
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id'), nullable=True)
    capability_id = db.Column(db.Integer, db.ForeignKey('capabilities.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    account = db.relationship('ConnectionAccount', back_populates='permissions')
    mcp_service = db.relationship('McpService', back_populates='permissions')
    app = db.relationship('Service', back_populates='permissions')
    capability = db.relationship('Capability', back_populates='permissions')
    
    def get_permission_level(self):
        """Get the level of permission: 'mcp_service', 'app', or 'capability'"""
        if self.mcp_service_id is not None:
            return 'mcp_service'
        elif self.app_id is not None:
            return 'app'
        elif self.capability_id is not None:
            return 'capability'
        return None
    
    def to_dict(self):
        result = {
            'id': self.id,
            'account_id': self.account_id,
            'permission_level': self.get_permission_level(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Add resource details based on permission level
        if self.mcp_service_id:
            result['mcp_service_id'] = self.mcp_service_id
            if self.mcp_service:
                result['mcp_service'] = {
                    'id': self.mcp_service.id,
                    'name': self.mcp_service.name,
                    'subdomain': self.mcp_service.subdomain
                }
        elif self.app_id:
            result['app_id'] = self.app_id
            if self.app:
                result['app'] = {
                    'id': self.app.id,
                    'name': self.app.name,
                    'mcp_service_id': self.app.mcp_service_id
                }
        elif self.capability_id:
            result['capability_id'] = self.capability_id
            if self.capability:
                capability_dict = self.capability.to_dict()
                if self.capability.service:
                    capability_dict['service_name'] = self.capability.service.name
                result['capability'] = capability_dict
        
        return result


class AdminSettings(db.Model):
    """管理者設定 - 言語設定などを保存"""
    __tablename__ = 'admin_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class McpServiceTemplate(db.Model):
    """MCPサービステンプレート - 標準搭載とカスタムテンプレート"""
    __tablename__ = 'mcp_service_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(20), nullable=False)  # 'builtin' or 'custom'
    service_type = db.Column(db.String(20), nullable=False)  # 'api' or 'mcp'
    description = db.Column(db.Text)
    common_headers = db.Column(db.Text)  # JSON string
    icon = db.Column(db.String(10))  # emoji icon
    category = db.Column(db.String(50))  # e.g., 'Communication', 'Cloud', 'AI', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    capability_templates = db.relationship('McpCapabilityTemplate', back_populates='service_template', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_type': self.template_type,
            'service_type': self.service_type,
            'description': self.description,
            'common_headers': json.loads(self.common_headers) if self.common_headers else {},
            'icon': self.icon,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_export_dict(self):
        """エクスポート用の辞書"""
        return {
            'name': self.name,
            'service_type': self.service_type,
            'description': self.description,
            'common_headers': json.loads(self.common_headers) if self.common_headers else {},
            'icon': self.icon,
            'category': self.category,
            'capabilities': [cap.to_export_dict() for cap in self.capability_templates]
        }


class McpCapabilityTemplate(db.Model):
    """Capabilityテンプレート - サービステンプレートに紐付く"""
    __tablename__ = 'mcp_capability_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    service_template_id = db.Column(db.Integer, db.ForeignKey('mcp_service_templates.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    capability_type = db.Column(db.String(50), nullable=False)  # 'tool', 'resource', 'prompt'
    url = db.Column(db.String(500))  # endpoint URL
    headers = db.Column(db.Text)  # JSON string
    body_params = db.Column(db.Text)  # JSON string
    template_content = db.Column(db.Text)  # prompt template
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_template = db.relationship('McpServiceTemplate', back_populates='capability_templates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'service_template_id': self.service_template_id,
            'name': self.name,
            'capability_type': self.capability_type,
            'url': self.url,
            'headers': json.loads(self.headers) if self.headers else {},
            'body_params': json.loads(self.body_params) if self.body_params else {},
            'template_content': self.template_content,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_export_dict(self):
        """エクスポート用の辞書"""
        return {
            'name': self.name,
            'capability_type': self.capability_type,
            'url': self.url,
            'headers': json.loads(self.headers) if self.headers else {},
            'body_params': json.loads(self.body_params) if self.body_params else {},
            'template_content': self.template_content,
            'description': self.description
        }


class Variable(db.Model):
    """変数管理 - API Key等の秘匿情報を管理"""
    __tablename__ = 'variables'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=False)  # 暗号化して保存
    value_type = db.Column(db.String(20), nullable=False, default='string')  # 'string' or 'number'
    source_type = db.Column(db.String(20), nullable=False, default='value')  # 'value' or 'env'
    env_var_name = db.Column(db.String(100))  # 環境変数名（source_type='env'の場合）
    description = db.Column(db.Text)
    is_secret = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def encrypt_value(value):
        """値を暗号化（簡易実装: Base64エンコード）"""
        import base64
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def decrypt_value(encrypted_value):
        """値を復号"""
        import base64
        return base64.b64decode(encrypted_value.encode('utf-8')).decode('utf-8')
    
    def set_value(self, plain_value):
        """値を暗号化して設定"""
        self.value = self.encrypt_value(plain_value)
    
    def get_value(self):
        """復号した値を取得（環境変数または直接値）"""
        if self.source_type == 'env':
            # 環境変数から取得
            import os
            return os.environ.get(self.env_var_name, '')
        else:
            # 暗号化された値を復号
            return self.decrypt_value(self.value)
    
    def get_typed_value(self):
        """型付きで値を取得（numberの場合は数値型で返す）"""
        plain_value = self.get_value()
        if self.value_type == 'number':
            try:
                # 整数か浮動小数点数かを判定
                if '.' in plain_value:
                    return float(plain_value)
                return int(plain_value)
            except ValueError:
                return plain_value  # 変換できない場合は文字列のまま
        return plain_value
    
    def to_dict(self, include_value=False):
        """辞書形式で返す"""
        result = {
            'id': self.id,
            'name': self.name,
            'value_type': self.value_type,
            'source_type': self.source_type,
            'env_var_name': self.env_var_name if self.source_type == 'env' else None,
            'description': self.description,
            'is_secret': self.is_secret,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_value:
            if self.source_type == 'env':
                result['value'] = f'[環境変数: {self.env_var_name}]'
            else:
                result['value'] = self.get_value()
        elif self.is_secret:
            result['value'] = '********'  # マスク表示
        else:
            result['value'] = self.get_value()
        return result

