"""
Database models for MCP Server
"""
import json
from datetime import datetime, UTC
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound


def utcnow():
    """UTC現在時刻を返すヘルパー関数（SQLAlchemyのdefault用）"""
    return datetime.now(UTC).replace(tzinfo=None)

db = SQLAlchemy()


def get_or_404(model, id, description=None):
    """
    db.session.get()を使ってオブジェクトを取得し、見つからなければ404エラーを発生させる。
    Flask-SQLAlchemyのquery.get_or_404()の代替（SQLAlchemy 2.0準拠）
    """
    obj = db.session.get(model, id)
    if obj is None:
        raise NotFound(description or f'{model.__name__} not found')
    return obj


class ConnectionAccount(db.Model):
    """接続アカウント - MCPサービスに接続するためのアカウント"""
    __tablename__ = 'connection_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bearer_token = db.Column(db.String(100), unique=True, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
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
    identifier = db.Column(db.String(50), unique=True, nullable=False)
    routing_type = db.Column(db.String(20), nullable=False, default='subdomain')  # 'subdomain' or 'path'
    description = db.Column(db.Text)
    access_control = db.Column(db.String(20), nullable=False, default='restricted')  # 'public' or 'restricted'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    apps = db.relationship('Service', back_populates='mcp_service', cascade='all, delete-orphan')
    permissions = db.relationship('AccountPermission', back_populates='mcp_service', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'identifier': self.identifier,
            'routing_type': self.routing_type,
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
    mcp_transport = db.Column(db.String(20), default='http')  # 'http' or 'stdio' (service_type='mcp'の場合)
    stdio_command = db.Column(db.String(500))  # stdio実行コマンド (例: 'npx', 'python')
    stdio_args = db.Column(db.Text)  # stdioコマンド引数 (JSON array, 例: ["-y", "@modelcontextprotocol/server-filesystem"])
    stdio_env = db.Column(db.Text)  # stdio環境変数 (JSON object, 例: {"API_KEY": "xxx"})
    stdio_cwd = db.Column(db.String(500))  # stdio作業ディレクトリ (オプション)
    common_headers = db.Column(db.Text)  # JSON string
    description = db.Column(db.Text)
    access_control = db.Column(db.String(20), nullable=False, default='public')  # 'public' or 'restricted'
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)  # 有効/無効フラグ
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
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
            'mcp_transport': self.mcp_transport or 'http',
            'stdio_command': self.stdio_command,
            'stdio_args': json.loads(self.stdio_args) if self.stdio_args else [],
            'stdio_env': json.loads(self.stdio_env) if self.stdio_env else {},
            'stdio_cwd': self.stdio_cwd,
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
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
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
    
    created_at = db.Column(db.DateTime, default=utcnow)
    
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
                    'identifier': self.mcp_service.identifier
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
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
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
    mcp_url = db.Column(db.String(500))  # MCP endpoint URL
    official_url = db.Column(db.String(500))  # Official documentation URL
    description = db.Column(db.Text)
    common_headers = db.Column(db.Text)  # JSON string
    icon = db.Column(db.String(10))  # emoji icon
    category = db.Column(db.String(50))  # e.g., 'Communication', 'Cloud', 'AI', etc.
    template_id = db.Column(db.String(100))  # Unique template identifier (e.g., 'github-mcp', 'slack-api')
    template_version = db.Column(db.String(20))  # Template version (e.g., '1.0.0')
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    capability_templates = db.relationship('McpCapabilityTemplate', back_populates='service_template', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_type': self.template_type,
            'service_type': self.service_type,
            'mcp_url': self.mcp_url,
            'official_url': self.official_url,
            'description': self.description,
            'common_headers': json.loads(self.common_headers) if self.common_headers else {},
            'icon': self.icon,
            'category': self.category,
            'template_id': self.template_id,
            'template_version': self.template_version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_export_dict(self):
        """エクスポート用の辞書"""
        result = {
            'name': self.name,
            'service_type': self.service_type,
            'mcp_url': self.mcp_url,
            'official_url': self.official_url,
            'description': self.description,
            'common_headers': json.loads(self.common_headers) if self.common_headers else {},
            'icon': self.icon,
            'category': self.category
        }
        
        # APIテンプレートの場合はcapabilitiesも含める
        if self.service_type == 'api' and self.capability_templates:
            result['capabilities'] = [cap.to_export_dict() for cap in self.capability_templates]
        
        return result


class McpCapabilityTemplate(db.Model):
    """MCPサービステンプレートのCapability定義（APIテンプレート用）"""
    __tablename__ = 'mcp_capability_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('mcp_service_templates.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    capability_type = db.Column(db.String(20), nullable=False)  # 'tool', 'resource', 'prompt'
    endpoint_path = db.Column(db.String(500))  # API endpoint path (relative to mcp_url)
    method = db.Column(db.String(10))  # HTTP method: GET, POST, PUT, DELETE, etc.
    description = db.Column(db.Text)
    headers = db.Column(db.Text)  # JSON string - 個別ヘッダー
    body_params = db.Column(db.Text)  # JSON string - リクエストボディパラメータ定義
    query_params = db.Column(db.Text)  # JSON string - クエリパラメータ定義
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    service_template = db.relationship('McpServiceTemplate', back_populates='capability_templates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'name': self.name,
            'capability_type': self.capability_type,
            'endpoint_path': self.endpoint_path,
            'method': self.method,
            'description': self.description,
            'headers': json.loads(self.headers) if self.headers else {},
            'body_params': json.loads(self.body_params) if self.body_params else {},
            'query_params': json.loads(self.query_params) if self.query_params else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_export_dict(self):
        """エクスポート用の辞書"""
        return {
            'name': self.name,
            'capability_type': self.capability_type,
            'endpoint_path': self.endpoint_path,
            'method': self.method,
            'description': self.description,
            'headers': json.loads(self.headers) if self.headers else {},
            'body_params': json.loads(self.body_params) if self.body_params else {},
            'query_params': json.loads(self.query_params) if self.query_params else {}
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
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
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
        # 環境変数の場合は常に環境変数名を表示
        if self.source_type == 'env':
            result['value'] = self.env_var_name
        elif include_value:
            result['value'] = self.get_value()
        elif self.is_secret:
            result['value'] = '********'  # マスク表示
        else:
            result['value'] = self.get_value()
        return result


class McpConnectionLog(db.Model):
    """MCP接続ログ - 監査用ログ"""
    __tablename__ = 'mcp_connection_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    duration_ms = db.Column(db.Integer, nullable=True)
    
    # Account info (nullable for public access)
    account_id = db.Column(db.Integer, db.ForeignKey('connection_accounts.id', ondelete='SET NULL'), nullable=True, index=True)
    account_name = db.Column(db.String(100), nullable=True)  # Snapshot for audit trail
    
    # Resource hierarchy
    mcp_service_id = db.Column(db.Integer, db.ForeignKey('mcp_services.id', ondelete='SET NULL'), nullable=True, index=True)
    mcp_service_name = db.Column(db.String(100), nullable=True)  # Snapshot
    app_id = db.Column(db.Integer, db.ForeignKey('apps.id', ondelete='SET NULL'), nullable=True)
    app_name = db.Column(db.String(100), nullable=True)  # Snapshot
    capability_id = db.Column(db.Integer, db.ForeignKey('capabilities.id', ondelete='SET NULL'), nullable=True)
    capability_name = db.Column(db.String(100), nullable=True)  # Snapshot
    
    # Request info
    mcp_method = db.Column(db.String(50), nullable=False, index=True)  # initialize, tools/list, tools/call, etc.
    tool_name = db.Column(db.String(100), nullable=True)  # Tool name for tools/call
    request_id = db.Column(db.String(100), nullable=True)  # JSON-RPC id
    
    # Request/Response bodies (size-limited, masked)
    request_body = db.Column(db.Text, nullable=True)
    response_body = db.Column(db.Text, nullable=True)
    
    # Status
    status_code = db.Column(db.Integer, nullable=True)  # HTTP-like status
    is_success = db.Column(db.Boolean, nullable=False, default=True)
    error_code = db.Column(db.Integer, nullable=True)  # JSON-RPC error code
    error_message = db.Column(db.Text, nullable=True)
    
    # Client info
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Access control
    access_control = db.Column(db.String(20), nullable=True)  # 'public' or 'restricted'
    
    # Relationships (optional, for eager loading)
    account = db.relationship('ConnectionAccount', foreign_keys=[account_id])
    mcp_service = db.relationship('McpService', foreign_keys=[mcp_service_id])
    app = db.relationship('Service', foreign_keys=[app_id])
    capability = db.relationship('Capability', foreign_keys=[capability_id])
    
    def to_dict(self, include_bodies=False):
        """辞書形式で返す"""
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_ms': self.duration_ms,
            'account_id': self.account_id,
            'account_name': self.account_name or '-',  # Public access shows '-'
            'mcp_service_id': self.mcp_service_id,
            'mcp_service_name': self.mcp_service_name,
            'app_id': self.app_id,
            'app_name': self.app_name,
            'capability_id': self.capability_id,
            'capability_name': self.capability_name,
            'mcp_method': self.mcp_method,
            'tool_name': self.tool_name,
            'request_id': self.request_id,
            'status_code': self.status_code,
            'is_success': self.is_success,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'access_control': self.access_control
        }
        if include_bodies:
            result['request_body'] = self.request_body
            result['response_body'] = self.response_body
        return result
    
    def to_csv_row(self):
        """CSV出力用の行を返す"""
        return [
            self.id,
            self.created_at.isoformat() if self.created_at else '',
            self.duration_ms or '',
            self.account_name or '-',
            self.mcp_service_name or '',
            self.app_name or '',
            self.capability_name or '',
            self.mcp_method,
            self.tool_name or '',
            'Success' if self.is_success else 'Error',
            self.error_message or '',
            self.ip_address or '',
            self.access_control or ''
        ]
    
    @staticmethod
    def csv_headers():
        """CSVヘッダー行を返す"""
        return [
            'ID', 'Created At', 'Duration (ms)', 'Account', 
            'MCP Service', 'App', 'Capability', 'Method', 'Tool Name',
            'Status', 'Error Message', 'IP Address', 'Access Control'
        ]


class AdminLoginLog(db.Model):
    """管理者ログイン履歴 - セキュリティ監査用"""
    __tablename__ = 'admin_login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)  # IPv6 compatible
    user_agent = db.Column(db.String(500))
    is_success = db.Column(db.Boolean, nullable=False)
    failure_reason = db.Column(db.String(255))  # 'invalid_username', 'invalid_password', 'account_locked'
    session_id = db.Column(db.String(255))  # Flask session ID (success only)
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'username': self.username,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_success': self.is_success,
            'failure_reason': self.failure_reason,
            'session_id': self.session_id
        }
    
    def to_csv_row(self):
        """CSV出力用の行を返す"""
        return [
            self.id,
            self.created_at.isoformat() if self.created_at else '',
            self.username,
            self.ip_address,
            'Success' if self.is_success else 'Failure',
            self.failure_reason or '',
            self.user_agent or ''
        ]
    
    @staticmethod
    def csv_headers():
        """CSVヘッダー行を返す"""
        return [
            'ID', 'Created At', 'Username', 'IP Address', 
            'Status', 'Failure Reason', 'User Agent'
        ]


class AdminActionLog(db.Model):
    """管理者操作履歴 - 全CRUD操作の監査証跡"""
    __tablename__ = 'admin_action_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    admin_username = db.Column(db.String(100), nullable=False, index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)  # 'create', 'update', 'delete'
    resource_type = db.Column(db.String(50), nullable=False, index=True)  # 'mcp_service', 'app', 'capability', etc.
    resource_id = db.Column(db.Integer)
    resource_name = db.Column(db.String(255))  # Snapshot
    changes = db.Column(db.Text)  # JSON: {'field': {'old': 'x', 'new': 'y'}}
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    def to_dict(self):
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'admin_username': self.admin_username,
            'action_type': self.action_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
        # Parse JSON changes if present
        if self.changes:
            try:
                result['changes'] = json.loads(self.changes)
            except:
                result['changes'] = self.changes
        else:
            result['changes'] = {}
        return result
    
    def to_csv_row(self):
        """CSV出力用の行を返す"""
        return [
            self.id,
            self.created_at.isoformat() if self.created_at else '',
            self.admin_username,
            self.action_type,
            self.resource_type,
            self.resource_id or '',
            self.resource_name or '',
            self.ip_address or ''
        ]
    
    @staticmethod
    def csv_headers():
        """CSVヘッダー行を返す"""
        return [
            'ID', 'Created At', 'Admin', 'Action', 
            'Resource Type', 'Resource ID', 'Resource Name', 'IP Address'
        ]


class LoginLockStatus(db.Model):
    """ログインロック状態管理 - ブルートフォース攻撃対策"""
    __tablename__ = 'login_lock_status'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, unique=True, index=True)
    failed_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True, index=True)
    last_attempt_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    
    def is_locked(self):
        """現在ロック中かどうか"""
        if self.locked_until is None:
            return False
        return datetime.now(UTC).replace(tzinfo=None) < self.locked_until
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'failed_attempts': self.failed_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None,
            'is_locked': self.is_locked(),
            'last_attempt_at': self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


