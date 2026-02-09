"""
Internationalization utilities
言語切り替え機能の提供
"""

# 翻訳辞書
TRANSLATIONS = {
    'ja': {
        # ヘッダー
        'app_title': 'MCP Server 管理画面',
        'logout': 'ログアウト',
        
        # パンくずリスト
        'breadcrumb_home': 'ホーム',
        'breadcrumb_service_list': 'サービス一覧',
        'breadcrumb_service_detail': 'サービス詳細',
        'breadcrumb_service_new': '新規登録',
        'breadcrumb_service_edit': '編集',
        'breadcrumb_capabilities': 'Capabilities',
        'breadcrumb_capability_detail': 'Capability詳細',
        'breadcrumb_account_list': '接続アカウント一覧',
        'breadcrumb_account_detail': 'アカウント詳細',
        
        # ダッシュボード
        'dashboard_title': 'ダッシュボード',
        'dashboard_description': '各機能へのアクセスはこちらから',
        'dashboard_service_title': '📡 サービス管理',
        'dashboard_service_description': 'MCPサービスの登録、編集、削除を行います。サブドメインや共通ヘッダーの設定が可能です。',
        'dashboard_account_title': '👥 接続アカウント管理',
        'dashboard_account_description': 'MCPサービスに接続するアカウントの登録、編集、削除を行います。Bearerトークンの発行が可能です。',
        
        # サービス一覧
        'service_list_title': 'サービス一覧',
        'service_list_description': '登録されているMCPサービスの管理',
        'service_new_button': '新規サービス登録',
        'service_empty': 'サービスが登録されていません',
        'service_subdomain': 'サブドメイン',
        'service_registered': '登録',
        
        # サービス詳細
        'service_detail_title': 'サービス詳細',
        'service_detail_description': 'サービスの詳細情報',
        'service_capabilities_button': 'Capabilities管理',
        'service_edit_button': '編集',
        'service_basic_info': '基本情報',
        'service_mcp_endpoint': 'MCPエンドポイント',
        'service_common_headers': '共通ヘッダー',
        'service_created': '登録日時',
        'service_updated': '更新日時',
        
        # サービス登録・編集
        'service_new_title': 'サービス新規登録',
        'service_new_description': '新しいMCPサービスを登録します',
        'service_edit_title': 'サービス編集',
        'service_edit_description': 'サービス情報を編集します',
        'service_name_label': 'サービス名',
        'service_subdomain_label': 'サブドメイン',
        'service_description_label': '説明',
        'service_type_label': 'サービスタイプ',
        'service_type_api': 'API',
        'service_type_mcp': 'MCP',
        'service_mcp_url_label': 'MCP URL',
        'service_register_button': '登録',
        'service_save_button': '保存',
        'service_cancel_button': 'キャンセル',
        
        # Capabilities
        'capabilities_title': 'Capabilities 一覧',
        'capabilities_description': 'このサービスで使用できるCapabilityの管理',
        'capability_new_button': '新規Capability登録',
        'capability_empty': 'Capabilityが登録されていません',
        'capability_detail_button': '詳細',
        'capability_edit_button': '編集',
        
        # Capability詳細
        'capability_detail_title': 'Capability 詳細',
        'capability_detail_description': 'Capabilityの詳細情報',
        'capability_basic_info': '基本情報',
        'capability_type_label': 'Capabilityタイプ',
        'capability_http_method': 'HTTPメソッド',
        'capability_url_label': '接続先URL',
        'capability_headers': 'ヘッダーパラメータ',
        'capability_body': 'Bodyパラメータ',
        
        # Capability登録・編集
        'capability_new_title': 'Capability 新規登録',
        'capability_new_description': '新しいCapabilityを登録します',
        'capability_edit_title': 'Capability 編集',
        'capability_edit_description': 'Capabilityの設定を編集します',
        'capability_name_label': 'Capability名',
        'capability_method_label': 'HTTPメソッド',
        'capability_description_label': '説明',
        'capability_headers_label': 'ヘッダーパラメータ',
        'capability_body_label': 'Bodyパラメータ',
        'capability_add_header': '+ ヘッダーを追加',
        'capability_add_param': '+ パラメータを追加',
        'capability_register_button': '登録',
        'capability_save_button': '保存',
        'capability_cancel_button': 'キャンセル',
        
        # 権限管理
        'permission_title': '接続可能アカウント管理',
        'permission_description': 'このCapabilityに接続できるアカウントを設定します',
        'permission_enabled': '接続可能アカウント',
        'permission_disabled': '未設定アカウント',
        'permission_count': '件',
        
        # アカウント
        'account_list_title': '接続アカウント一覧',
        'account_list_description': 'MCPサービスに接続できるアカウントの管理',
        'account_new_button': '新規アカウント登録',
        'account_empty': '接続アカウントが登録されていません',
        'account_detail_title': 'アカウント詳細',
        'account_detail_description': 'アカウントの詳細情報とCapability一覧',
        'account_new_title': '接続アカウント新規登録',
        'account_new_description': 'MCPサービスに接続できる新しいアカウントを登録します',
        'account_name_label': 'アカウント名',
        'account_notes_label': '備考',
        'account_bearer_token': 'Bearerトークン',
        'account_regenerate_token': 'トークン再発行',
        'account_capabilities': 'このアカウントが使用できるCapability',
        'account_edit_info': 'アカウント情報の編集',
        
        # ボタン
        'button_details': '詳細',
        'button_edit': '編集',
        'button_delete': '削除',
        'button_save': '保存',
        'button_cancel': 'キャンセル',
        'button_register': '登録',
        'btn_save': '保存',
        'btn_back': '戻る',
        
        # 共通
        'loading': '読み込み中...',
        
        # ログ検索
        'log_filter_search': '検索',
        'log_detail_title': 'ログ詳細',
        
        # リソース使用例
        'resource_usage_feature_global': 'グローバルリソース参照',
        'resource_usage_feature_global_desc': '登録済みのリソースを参照できます',
        'resource_usage_feature_uri': 'リソースURI',
        'resource_usage_feature_uri_desc': 'リソースを一意に識別するURIを設定します',
        'resource_usage_feature_access': 'アクセス制御',
        'resource_usage_feature_access_desc': 'リソースへのアクセス権限を設定できます',
        'resource_usage_feature_mime': 'MIMEタイプ',
        'resource_usage_feature_mime_desc': 'リソースのコンテンツタイプを指定します',
        'resource_usage_example_policy': '利用規約・ポリシー',
        'resource_usage_example_faq': 'FAQ・ナレッジベース',
        'resource_usage_example_config': '設定ファイル・環境変数',
        'resource_usage_example_template': 'プロンプトテンプレート',
        
        # Capability テンプレート
        'capability_template_hint': 'プロンプトテンプレートの使用方法',
        
        # メッセージ
        'required_field': '必須',
    },
    'en': {
        # Header
        'app_title': 'MCP Server Admin',
        'logout': 'Logout',
        
        # Breadcrumb
        'breadcrumb_home': 'Home',
        'breadcrumb_service_list': 'Services',
        'breadcrumb_service_detail': 'Service Detail',
        'breadcrumb_service_new': 'New',
        'breadcrumb_service_edit': 'Edit',
        'breadcrumb_capabilities': 'Capabilities',
        'breadcrumb_capability_detail': 'Capability Detail',
        'breadcrumb_account_list': 'Accounts',
        'breadcrumb_account_detail': 'Account Detail',
        
        # Dashboard
        'dashboard_title': 'Dashboard',
        'dashboard_description': 'Access to each function',
        'dashboard_service_title': '📡 Service Management',
        'dashboard_service_description': 'Register, edit, and delete MCP services. Configure subdomains and common headers.',
        'dashboard_account_title': '👥 Account Management',
        'dashboard_account_description': 'Register, edit, and delete accounts that can connect to MCP services. Issue Bearer tokens.',
        
        # Service List
        'service_list_title': 'Services',
        'service_list_description': 'Management of registered MCP services',
        'service_new_button': 'New Service',
        'service_empty': 'No services registered',
        'service_subdomain': 'Subdomain',
        'service_registered': 'Registered',
        
        # Service Detail
        'service_detail_title': 'Service Detail',
        'service_detail_description': 'Service information',
        'service_capabilities_button': 'Manage Capabilities',
        'service_edit_button': 'Edit',
        'service_basic_info': 'Basic Information',
        'service_mcp_endpoint': 'MCP Endpoint',
        'service_common_headers': 'Common Headers',
        'service_created': 'Created',
        'service_updated': 'Updated',
        
        # Service New/Edit
        'service_new_title': 'New Service',
        'service_new_description': 'Register a new MCP service',
        'service_edit_title': 'Edit Service',
        'service_edit_description': 'Edit service information',
        'service_name_label': 'Service Name',
        'service_subdomain_label': 'Subdomain',
        'service_description_label': 'Description',
        'service_type_label': 'Service Type',
        'service_type_api': 'API',
        'service_type_mcp': 'MCP',
        'service_mcp_url_label': 'MCP URL',
        'service_register_button': 'Register',
        'service_save_button': 'Save',
        'service_cancel_button': 'Cancel',
        
        # Capabilities
        'capabilities_title': 'Capabilities',
        'capabilities_description': 'Management of capabilities available in this service',
        'capability_new_button': 'New Capability',
        'capability_empty': 'No capabilities registered',
        'capability_detail_button': 'Details',
        'capability_edit_button': 'Edit',
        
        # Capability Detail
        'capability_detail_title': 'Capability Detail',
        'capability_detail_description': 'Capability information',
        'capability_basic_info': 'Basic Information',
        'capability_type_label': 'Capability Type',
        'capability_http_method': 'HTTP Method',
        'capability_url_label': 'URL',
        'capability_headers': 'Header Parameters',
        'capability_body': 'Body Parameters',
        
        # Capability New/Edit
        'capability_new_title': 'New Capability',
        'capability_new_description': 'Register a new capability',
        'capability_edit_title': 'Edit Capability',
        'capability_edit_description': 'Edit capability settings',
        'capability_name_label': 'Capability Name',
        'capability_method_label': 'HTTP Method',
        'capability_description_label': 'Description',
        'capability_headers_label': 'Header Parameters',
        'capability_body_label': 'Body Parameters',
        'capability_add_header': '+ Add Header',
        'capability_add_param': '+ Add Parameter',
        'capability_register_button': 'Register',
        'capability_save_button': 'Save',
        'capability_cancel_button': 'Cancel',
        
        # Permissions
        'permission_title': 'Account Permissions',
        'permission_description': 'Configure accounts that can access this capability',
        'permission_enabled': 'Enabled Accounts',
        'permission_disabled': 'Disabled Accounts',
        'permission_count': 'items',
        
        # Accounts
        'account_list_title': 'Accounts',
        'account_list_description': 'Management of accounts that can connect to MCP services',
        'account_new_button': 'New Account',
        'account_empty': 'No accounts registered',
        'account_detail_title': 'Account Detail',
        'account_detail_description': 'Account information and capabilities',
        'account_new_title': 'New Account',
        'account_new_description': 'Register a new account that can connect to MCP services',
        'account_name_label': 'Account Name',
        'account_notes_label': 'Notes',
        'account_bearer_token': 'Bearer Token',
        'account_regenerate_token': 'Regenerate Token',
        'account_capabilities': 'Capabilities available to this account',
        'account_edit_info': 'Edit Account Information',
        
        # Buttons
        'button_details': 'Details',
        'button_edit': 'Edit',
        'button_delete': 'Delete',
        'button_save': 'Save',
        'button_cancel': 'Cancel',
        'button_register': 'Register',
        'btn_save': 'Save',
        'btn_back': 'Back',
        
        # Common
        'loading': 'Loading...',
        
        # Log search
        'log_filter_search': 'Search',
        'log_detail_title': 'Log Detail',
        
        # Resource usage
        'resource_usage_feature_global': 'Global Resource Reference',
        'resource_usage_feature_global_desc': 'Reference registered resources',
        'resource_usage_feature_uri': 'Resource URI',
        'resource_usage_feature_uri_desc': 'Set a unique URI to identify the resource',
        'resource_usage_feature_access': 'Access Control',
        'resource_usage_feature_access_desc': 'Configure access permissions for the resource',
        'resource_usage_feature_mime': 'MIME Type',
        'resource_usage_feature_mime_desc': 'Specify the content type of the resource',
        'resource_usage_example_policy': 'Terms & Policies',
        'resource_usage_example_faq': 'FAQ & Knowledge Base',
        'resource_usage_example_config': 'Config Files & Environment Variables',
        'resource_usage_example_template': 'Prompt Templates',
        
        # Capability template
        'capability_template_hint': 'How to use prompt templates',
        
        # Messages
        'required_field': 'Required',
    }
}


def get_translation(key, lang='ja'):
    """指定された言語の翻訳を取得"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['ja']).get(key, key)


def get_all_translations(lang='ja'):
    """指定された言語の全翻訳を取得"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['ja'])
