/**
 * 国際化(i18n)ユーティリティ
 * 言語切り替え機能とブラウザ言語検出
 */

const translations = {
    ja: {
        // ヘッダー
        app_title: 'Accel MCP',
        logout: 'ログアウト',
        
        // パンくずリスト
        breadcrumb_home: 'ホーム',
        breadcrumb_app_list: 'アプリ一覧',
        breadcrumb_app_detail: 'アプリ詳細',
        breadcrumb_app_new: '新規登録',
        breadcrumb_app_edit: '編集',
        breadcrumb_capabilities: 'Capabilities',
        breadcrumb_capability_detail: 'Capability詳細',
        breadcrumb_account_list: '接続アカウント一覧',
        breadcrumb_account_detail: 'アカウント詳細',
        
        // ボタン
        button_details: '詳細',
        button_edit: '編集',
        button_delete: '削除',
        button_save: '保存',
        button_cancel: 'キャンセル',
        button_register: '登録',
        button_add_header: '+ ヘッダーを追加',
        button_add_permission: '+ 権限を追加',
        button_copy: 'コピー',
        button_copied: 'コピーしました',
        button_close: '閉じる',
        button_back: '戻る',
        button_validate_json: 'JSON構造チェック',
        button_format_json: '整形',
        
        // Copy/Paste
        copy_failed: 'コピーに失敗しました',
        
        // JSON validation
        json_valid: 'JSON構造は正しいです',
        json_invalid: 'JSON構造にエラーがあります',
        json_formatted: 'JSONを整形しました',
        
        // ダッシュボード
        dashboard_title: 'ダッシュボード',
        dashboard_description: '各機能へのアクセスはこちらから',
        mcp_service_card_title: '🌐 MCPサービス管理',
        mcp_service_card_description: 'MCPサービスの登録、編集、削除を行います。サブドメインの設定と複数のアプリを管理できます。',
        app_card_title: '📡 アプリ管理',
        app_card_description: 'MCPアプリの登録、編集、削除を行います。サブドメインや共通ヘッダーの設定が可能です。',
        account_card_title: '👥 接続アカウント管理',
        account_card_description: 'MCPアプリに接続するアカウントの登録、編集、削除を行います。Bearerトークンの発行が可能です。',
        mcp_template_card_title: '📦 テンプレート管理',
        mcp_template_card_description: 'APIアプリの標準テンプレートとカスタムテンプレートを管理します。テンプレートからアプリを簡単に作成できます。',
        
        // MCPサービス一覧
        mcp_service_list_title: 'MCPサービス一覧',
        mcp_service_list_desc: '登録されているMCPサービスの管理',
        mcp_service_new_button: '新規MCPサービス登録',
        mcp_service_empty: 'MCPサービスが登録されていません',
        mcp_service_subdomain: 'サブドメイン',
        mcp_service_apps_count: 'アプリ数',
        mcp_service_delete_confirm: 'このMCPサービスを削除してもよろしいですか？配下のアプリもすべて削除されます。',
        
        // MCPサービス詳細
        mcp_service_detail_title: 'MCPサービス詳細',
        mcp_service_detail_desc: 'MCPサービスの詳細情報',
        mcp_service_apps_manage: 'アプリ管理',
        mcp_service_apps_button: 'アプリ',
        mcp_service_basic_info: '基本情報',
        mcp_service_subdomain_label: 'サブドメイン',
        mcp_service_mcp_endpoint: 'MCPエンドポイント',
        mcp_service_apps_list: '配下のアプリ',
        
        // MCPサービス新規登録
        mcp_service_new_title: 'MCPサービス新規登録',
        mcp_service_new_desc: '新しいMCPサービスを登録します',
        mcp_service_name_label: 'サービス名',
        mcp_service_subdomain_input: 'サブドメイン',
        mcp_service_subdomain_hint: '小文字英数字とハイフンのみ使用可能',
        mcp_service_subdomain_url_hint: 'MCP接続URL: http://{subdomain}.lvh.me:5001/mcp (例: http://myservice.lvh.me:5001/mcp)',
        mcp_service_description_label: '説明',
        mcp_service_register_failed: '登録に失敗しました',
        mcp_service_update_failed: '更新に失敗しました',
        
        // MCPサービス編集
        mcp_service_edit_title: 'MCPサービス編集',
        mcp_service_edit_desc: 'MCPサービス情報を編集します',
        
        // テンプレート一覧
        mcp_template_list_title: 'テンプレート一覧',
        mcp_template_list_desc: 'サービステンプレートの管理',
        mcp_template_tab_api: 'WebService(API)',
        mcp_template_tab_mcp: 'WebService(MCP)',
        mcp_template_tab_custom: 'カスタム',
        mcp_template_new_button: '新規カスタムテンプレート',
        mcp_template_new_title: '新規カスタムテンプレート',
        mcp_template_new_description: 'カスタムAPIテンプレートを作成します',
        mcp_template_edit_title: 'テンプレート編集',
        mcp_template_edit_description: 'カスタムテンプレートを編集します',
        mcp_template_detail_title: 'テンプレート詳細',
        mcp_template_empty: 'テンプレートがありません',
        mcp_template_category: 'カテゴリ',
        mcp_template_capabilities_count: 'Capabilities',
        mcp_template_capabilities_list: 'Capabilities一覧',
        mcp_template_use_button: '使用する',
        mcp_template_use_modal_title: 'テンプレートを使用',
        mcp_template_use_modal_description: 'このテンプレートからサービスを作成します。サブドメインを入力してください。',
        mcp_template_use_success_title: '登録しました',
        mcp_template_use_go_to_services: 'サービス一覧へ',
        mcp_template_export_button: 'エクスポート',
        mcp_template_import_button: 'インポート',
        mcp_template_import_title: 'テンプレートをインポート',
        mcp_template_import_description: 'エクスポートしたJSONファイルをドラッグ&ドロップまたは選択してください',
        mcp_template_import_drop_hint: 'ここにJSONファイルをドロップ',
        mcp_template_import_or: 'または',
        mcp_template_import_select_file: 'ファイルを選択',
        button_clear: 'クリア',
        mcp_template_import_button: 'インポート',
        mcp_template_delete_confirm: 'このテンプレートを削除してもよろしいですか?',
        mcp_template_builtin_cannot_edit: '標準搭載テンプレートは編集できません',
        mcp_template_builtin_cannot_delete: '標準搭載テンプレートは削除できません',
        mcp_template_name_label: 'テンプレート名',
        mcp_template_icon_label: 'アイコン',
        mcp_template_icon_hint: '絵文字1文字（省略可）',
        mcp_template_category_label: 'カテゴリ',
        mcp_template_description_label: '説明',
        mcp_template_type_label: 'テンプレートタイプ',
        mcp_template_basic_info: '基本情報',
        mcp_template_common_headers: '共通ヘッダー',
        mcp_template_capabilities_button: 'Capabilities',
        
        // Capability管理
        capability_management_title: 'Capabilities管理',
        capability_management_description: 'テンプレートのCapabilityを管理します',
        capability_new_button: '新規Capability',
        capability_basic_info: '基本情報',
        capability_name_label: '名前',
        capability_type_label: 'タイプ',
        capability_url_label: 'URL',
        capability_headers_label: 'ヘッダー',
        capability_body_params_label: 'ボディパラメータ',
        capability_mcp_template_content_label: 'テンプレートコンテンツ',
        capability_delete_confirm: 'このCapabilityを削除してもよろしいですか?',
        capability_empty: 'Capabilitiesが登録されていません',
        capability_no_headers: 'ヘッダーが設定されていません',
        capability_no_params: 'ボディパラメータが設定されていません',
        status_enabled: '有効',
        status_disabled: '無効',
        
        // アプリ一覧
        app_list_title: 'アプリ一覧',
        app_list_desc: '登録されているMCPアプリの管理',
        app_new_button: '新規アプリ登録',
        app_empty: 'アプリが登録されていません',
        app_subdomain: 'サブドメイン',
        app_registered: '登録',
        app_capabilities_button: 'Capabilities',
        app_delete_confirm: 'このアプリを削除してもよろしいですか?',
        
        // アプリ詳細
        app_detail_title: 'アプリ詳細',
        app_detail_desc: 'アプリの詳細情報',
        app_capabilities_manage: 'Capabilities管理',
        app_basic_info: '基本情報',
        app_subdomain_label: 'サブドメイン',
        app_mcp_endpoint: 'MCPエンドポイント',
        app_registered_at: '登録日時',
        app_updated_at: '更新日時',
        app_common_headers: '共通ヘッダー',
        
        // アプリ新規登録
        app_new_title: 'アプリ新規登録',
        app_new_desc: '新しいMCPアプリを登録します',
        app_name_label: 'アプリ名',
        app_subdomain_input: 'サブドメイン',
        app_subdomain_hint: '小文字英数字とハイフンのみ使用可能',
        app_subdomain_pattern_hint: '小文字英数字とハイフンのみ使用可能',
        app_subdomain_url_hint: 'MCP接続URL: http://{subdomain}.lvh.me:5001/mcp (例: http://myapp.lvh.me:5001/mcp)',
        app_description_label: '説明',
        app_type_label: 'アプリタイプ',
        app_type_api: 'API (手動登録)',
        app_type_mcp: 'MCP (自動検出)',
        app_mcp_url_label: 'MCP接続URL',
        app_mcp_url_hint: 'MCPサーバーのSSEエンドポイントURLを入力してください',
        app_test_connection: '接続テスト',
        app_mcp_url_required: 'MCP接続URLを入力してください',
        app_testing_connection: '接続テスト中...',
        app_connection_success: '接続成功',
        app_connection_failed: '接続失敗',
        app_connection_error: '接続エラー',
        app_common_headers_label: '共通ヘッダー',
        app_common_headers_hint: '全てのCapabilityで使用される共通ヘッダー',
        app_register_failed: '登録に失敗しました',
        app_update_failed: '更新に失敗しました',
        
        // アプリ編集
        app_edit_title: 'アプリ編集',
        app_edit_desc: 'アプリ情報を編集します',
        
        // Capabilities一覧
        capabilities_title: 'Capabilities一覧',
        capabilities_desc: 'サービスのCapability管理',
        capability_new_button: '新規Capability登録',
        capability_empty: 'Capabilityが登録されていません',
        capability_type: 'タイプ',
        capability_endpoint: 'エンドポイント',
        capability_method: 'メソッド',
        capability_delete_confirm: 'このCapabilityを削除してもよろしいですか?',
        
        // Capability詳細
        capability_detail_title: 'Capability詳細',
        capability_detail_desc: 'Capabilityの詳細情報',
        capability_basic_info: '基本情報',
        capability_name_label: 'Capability名',
        capability_type_label: 'タイプ',
        capability_type_detail: 'Capabilityタイプ',
        capability_method_label: 'HTTPメソッド',
        capability_url_label: '接続先URL',
        capability_endpoint_label: 'エンドポイント',
        capability_input_schema: '入力スキーマ',
        capability_output_schema: '出力スキーマ',
        capability_headers: 'ヘッダー',
        capability_headers_params: 'ヘッダーパラメータ',
        capability_body_params_label: 'Bodyパラメータ',
        capability_registered_at: '登録日時',
        capability_updated_at: '更新日時',
        
        // Capability新規登録
        capability_new_title: '新規Capability登録',
        capability_new_description: '新しいCapabilityを作成します',
        capability_new_desc: '新しいCapabilityを登録します',
        capability_input_schema_label: '入力スキーマ (JSON)',
        capability_output_schema_label: '出力スキーマ (JSON)',
        capability_headers_label: 'ヘッダー',
        capability_register_failed: '登録に失敗しました',
        capability_update_failed: '更新に失敗しました',
        capability_mcp_tool_name: 'MCP Toolとして公開される名前',
        capability_http_method: 'HTTPメソッド',
        capability_connection_url: '接続先URL',
        capability_header_params: 'ヘッダーパラメータ',
        capability_header_params_hint: '個別のヘッダーパラメータ（アプリ共通ヘッダーに追加されます）',
        capability_body_params: 'Bodyパラメータ',
        capability_body_params_add: '+ パラメータを追加',
        capability_body_params_hint: 'クエリパラメータまたはフォームデータ',
        capability_body_json_hint: 'JSON形式のリクエストボディ',
        capability_account_management: '接続可能アカウント管理',
        capability_account_management_desc: 'このCapabilityに接続できるアカウントを設定します',
        capability_enabled_accounts: '接続可能アカウント',
        capability_disabled_accounts: '未設定アカウント',
        capability_items_count: '件',
        capability_url_hint: 'APIエンドポイントのURL',
        capability_mcp_template_hint: 'Promptタイプの場合に使用します',
        capability_description_label: '説明',
        capability_header_key: 'キー',
        capability_header_value: '値',
        capability_param_key: 'キー',
        capability_param_value: '値',
        button_add_header: '+ ヘッダーを追加',
        button_add_param: '+ パラメータを追加',
        button_remove: '削除',
        capability_name_placeholder: '例: get_user_info',
        capability_url_placeholder: '例: https://api.example.com/users/{id}',
        capability_description_placeholder: 'このCapabilityの説明を入力してください',
        capability_mcp_template_content_placeholder: 'Promptタイプの場合、テンプレートコンテンツを入力してください',
        capability_registered: '登録しました',
        
        // Capability編集
        capability_edit_title: 'Capability編集',
        capability_edit_desc: 'Capability情報を編集します',
        capability_json_error: 'JSON形式が正しくありません',
        
        // アカウント一覧
        account_list_title: '接続アカウント一覧',
        account_list_desc: 'MCP接続に使用するアカウント管理',
        account_new_button: '新規アカウント登録',
        account_empty: 'アカウントが登録されていません',
        account_service: 'サービス',
        account_permissions: '権限',
        account_created: '作成日',
        account_delete_confirm: 'このアカウントを削除してもよろしいですか?',
        
        // アカウント詳細
        account_detail_title: 'アカウント詳細',
        account_detail_desc: 'アカウントの詳細情報',
        account_capabilities_title: 'このアカウントが使用できるCapability',
        account_edit_info: 'アカウント情報の編集',
        account_basic_info: '基本情報',
        account_name_label: 'アカウント名',
        account_notes_label: '備考',
        account_service_label: 'サービス',
        account_api_key_label: 'APIキー',
        account_permissions_label: '権限設定',
        account_capability_label: 'Capability',
        account_all_capabilities: '全てのCapability',
        account_permission_type: '権限タイプ',
        account_permission_allow: '許可',
        account_permission_deny: '拒否',
        account_created_at: '作成日時',
        account_updated_at: '更新日時',
        account_bearer_token: 'Bearer トークン',
        account_copy_token: 'コピー',
        account_token_copied: 'トークンをコピーしました',
        account_regenerate_token: 'トークン再発行',
        account_regenerate_confirm: 'トークンを再発行してもよろしいですか? 既存のトークンは無効になります。',
        account_token_regenerated: 'トークンを再発行しました',
        account_update_success: '保存しました',
        account_no_capabilities: 'Capabilityが設定されていません',
        account_unknown_service: '不明なサービス',
        
        // アカウント新規登録
        account_new_title: '新規アカウント登録',
        account_new_desc: '新しい接続アカウントを登録します',
        account_notes_placeholder: 'このアカウントに関する備考を記入できます',
        account_permissions_hint: 'Capabilityごとにアクセス権限を設定できます',
        account_register_failed: '登録に失敗しました',
        account_update_failed: '更新に失敗しました',
        
        // 共通フォーム
        form_required: '必須',
        form_optional: '任意',
        form_key_placeholder: 'キー (例: Authorization)',
        form_value_placeholder: '値 (例: Bearer xxx)',
        form_json_placeholder: 'JSON形式で入力',
        
        // メッセージ
        error_unknown: '不明なエラー',
        confirm_delete: '削除してもよろしいですか?',
    },
    en: {
        // Header
        app_title: 'Accel MCP',
        logout: 'Logout',
        
        // Breadcrumb
        breadcrumb_home: 'Home',
        breadcrumb_app_list: 'Apps',
        breadcrumb_app_detail: 'App Detail',
        breadcrumb_app_new: 'New',
        breadcrumb_app_edit: 'Edit',
        breadcrumb_capabilities: 'Capabilities',
        breadcrumb_capability_detail: 'Capability Detail',
        breadcrumb_account_list: 'Accounts',
        breadcrumb_account_detail: 'Account Detail',
        
        // Buttons
        button_details: 'Details',
        button_edit: 'Edit',
        button_delete: 'Delete',
        button_save: 'Save',
        button_cancel: 'Cancel',
        button_register: 'Register',
        button_add_header: '+ Add Header',
        button_add_permission: '+ Add Permission',
        button_copy: 'Copy',
        button_copied: 'Copied',
        button_close: 'Close',
        button_back: 'Back',
        button_validate_json: 'Validate JSON',
        button_format_json: 'Format',
        
        // Copy/Paste
        copy_failed: 'Failed to copy',
        
        // JSON validation
        json_valid: 'JSON structure is valid',
        json_invalid: 'Invalid JSON structure',
        json_formatted: 'JSON formatted successfully',
        
        // Dashboard
        dashboard_title: 'Dashboard',
        dashboard_description: 'Access to each function',
        mcp_service_card_title: '🌐 MCP Service Management',
        mcp_service_card_description: 'Register, edit, and delete MCP services. Configure subdomains and manage multiple apps.',
        app_card_title: '📡 App Management',
        app_card_description: 'Register, edit, and delete MCP apps. Configure subdomains and common headers.',
        account_card_title: '👥 Account Management',
        account_card_description: 'Register, edit, and delete accounts that can connect to MCP apps. Issue Bearer tokens.',
        mcp_template_card_title: '📦 Template Management',
        mcp_template_card_description: 'Manage built-in and custom API app templates. Easily create apps from templates.',
        
        // MCP Service List
        mcp_service_list_title: 'MCP Services',
        mcp_service_list_desc: 'Manage registered MCP services',
        mcp_service_new_button: 'New MCP Service',
        mcp_service_empty: 'No MCP services registered',
        mcp_service_subdomain: 'Subdomain',
        mcp_service_apps_count: 'Apps',
        mcp_service_delete_confirm: 'Are you sure you want to delete this MCP service? All apps under it will also be deleted.',
        
        // MCP Service Detail
        mcp_service_detail_title: 'MCP Service Detail',
        mcp_service_detail_desc: 'MCP service details',
        mcp_service_apps_manage: 'Manage Apps',
        mcp_service_apps_button: 'Apps',
        mcp_service_basic_info: 'Basic Information',
        mcp_service_subdomain_label: 'Subdomain',
        mcp_service_mcp_endpoint: 'MCP Endpoint',
        mcp_service_apps_list: 'Apps',
        
        // MCP Service New
        mcp_service_new_title: 'New MCP Service',
        mcp_service_new_desc: 'Register a new MCP service',
        mcp_service_name_label: 'Service Name',
        mcp_service_subdomain_input: 'Subdomain',
        mcp_service_subdomain_hint: 'Only lowercase alphanumeric characters and hyphens allowed',
        mcp_service_subdomain_url_hint: 'MCP connection URL: http://{subdomain}.lvh.me:5001/mcp (e.g., http://myservice.lvh.me:5001/mcp)',
        mcp_service_description_label: 'Description',
        mcp_service_register_failed: 'Registration failed',
        mcp_service_update_failed: 'Update failed',
        
        // MCP Service Edit
        mcp_service_edit_title: 'Edit MCP Service',
        mcp_service_edit_desc: 'Edit MCP service information',
        
        // Template List
        mcp_template_list_title: 'Template List',
        mcp_template_list_desc: 'Service template management',
        mcp_template_tab_api: 'WebService(API)',
        mcp_template_tab_mcp: 'WebService(MCP)',
        mcp_template_tab_custom: 'Custom',
        mcp_template_new_button: 'New Custom Template',
        mcp_template_new_title: 'New Custom Template',
        mcp_template_new_description: 'Create a custom API template',
        mcp_template_edit_title: 'Edit Template',
        mcp_template_edit_description: 'Edit custom template',
        mcp_template_detail_title: 'Template Detail',
        mcp_template_empty: 'No templates available',
        mcp_template_category: 'Category',
        mcp_template_capabilities_count: 'Capabilities',
        mcp_template_capabilities_list: 'Capabilities List',
        mcp_template_use_button: 'Use',
        mcp_template_use_modal_title: 'Use Template',
        mcp_template_use_modal_description: 'Create a service from this template. Please enter a subdomain.',
        mcp_template_use_success_title: 'Registered Successfully',
        mcp_template_use_go_to_services: 'Go to Services',
        mcp_template_export_button: 'Export',
        mcp_template_import_button: 'Import',
        mcp_template_import_title: 'Import Template',
        mcp_template_import_description: 'Drag and drop or select an exported JSON file',
        mcp_template_import_drop_hint: 'Drop JSON file here',
        mcp_template_import_or: 'or',
        mcp_template_import_select_file: 'Select File',
        button_clear: 'Clear',
        mcp_template_import_button: 'Import',
        mcp_template_delete_confirm: 'Are you sure you want to delete this template?',
        mcp_template_builtin_cannot_edit: 'Built-in templates cannot be edited',
        mcp_template_builtin_cannot_delete: 'Built-in templates cannot be deleted',
        mcp_template_name_label: 'Template Name',
        mcp_template_icon_label: 'Icon',
        mcp_template_icon_hint: 'Emoji character (optional)',
        mcp_template_category_label: 'Category',
        mcp_template_description_label: 'Description',
        mcp_template_type_label: 'Template Type',
        mcp_template_basic_info: 'Basic Information',
        mcp_template_common_headers: 'Common Headers',
        mcp_template_capabilities_button: 'Capabilities',
        
        // Capability Management
        capability_management_title: 'Capability Management',
        capability_management_description: 'Manage template capabilities',
        capability_new_button: 'New Capability',
        capability_basic_info: 'Basic Information',
        capability_name_label: 'Name',
        capability_type_label: 'Type',
        capability_url_label: 'URL',
        capability_headers_label: 'Headers',
        capability_body_params_label: 'Body Parameters',
        capability_mcp_template_content_label: 'Template Content',
        capability_delete_confirm: 'Are you sure you want to delete this capability?',
        capability_empty: 'No capabilities registered',
        capability_no_headers: 'No headers configured',
        capability_no_params: 'No body parameters configured',
        status_enabled: 'Enabled',
        status_disabled: 'Disabled',
        
        // App List
        app_list_title: 'Apps',
        app_list_desc: 'Manage registered MCP apps',
        app_new_button: 'New App',
        app_empty: 'No apps registered',
        app_subdomain: 'Subdomain',
        app_registered: 'Registered',
        app_capabilities_button: 'Capabilities',
        app_delete_confirm: 'Are you sure you want to delete this app?',
        
        // App Detail
        app_detail_title: 'App Detail',
        app_detail_desc: 'App information',
        app_capabilities_manage: 'Manage Capabilities',
        app_basic_info: 'Basic Information',
        app_subdomain_label: 'Subdomain',
        app_mcp_endpoint: 'MCP Endpoint',
        app_registered_at: 'Registered At',
        app_updated_at: 'Updated At',
        app_common_headers: 'Common Headers',
        
        // App New
        app_new_title: 'New App',
        app_new_desc: 'Register a new MCP app',
        app_name_label: 'App Name',
        app_subdomain_input: 'Subdomain',
        app_subdomain_hint: 'Only lowercase alphanumeric characters and hyphens allowed',
        app_subdomain_pattern_hint: 'Only lowercase alphanumeric characters and hyphens allowed',
        app_subdomain_url_hint: 'MCP Connection URL: http://{subdomain}.lvh.me:5001/mcp (e.g., http://myapp.lvh.me:5001/mcp)',
        app_description_label: 'Description',
        app_type_label: 'App Type',
        app_type_api: 'API (Manual Registration)',
        app_type_mcp: 'MCP (Auto Detection)',
        app_mcp_url_label: 'MCP Connection URL',
        app_mcp_url_hint: 'Enter the SSE endpoint URL of the MCP server',
        app_test_connection: 'Test Connection',
        app_mcp_url_required: 'Please enter MCP connection URL',
        app_testing_connection: 'Testing connection...',
        app_connection_success: 'Connection successful',
        app_connection_failed: 'Connection failed',
        app_connection_error: 'Connection error',
        app_common_headers_label: 'Common Headers',
        app_common_headers_hint: 'Headers used by all capabilities',
        app_register_failed: 'Registration failed',
        app_update_failed: 'Update failed',
        
        // App Edit
        app_edit_title: 'Edit App',
        app_edit_desc: 'Edit app information',
        
        // Capabilities List
        capabilities_title: 'Capabilities',
        capabilities_desc: 'Manage service capabilities',
        capability_new_button: 'New Capability',
        capability_empty: 'No capabilities registered',
        capability_type: 'Type',
        capability_endpoint: 'Endpoint',
        capability_method: 'Method',
        capability_delete_confirm: 'Are you sure you want to delete this capability?',
        
        // Capability Detail
        capability_detail_title: 'Capability Detail',
        capability_detail_desc: 'Capability information',
        capability_basic_info: 'Basic Information',
        capability_name_label: 'Capability Name',
        capability_type_label: 'Type',
        capability_type_detail: 'Capability Type',
        capability_method_label: 'HTTP Method',
        capability_url_label: 'Connection URL',
        capability_endpoint_label: 'Endpoint',
        capability_input_schema: 'Input Schema',
        capability_output_schema: 'Output Schema',
        capability_headers: 'Headers',
        capability_headers_params: 'Header Parameters',
        capability_body_params_label: 'Body Parameters',
        capability_registered_at: 'Registered At',
        capability_updated_at: 'Updated At',
        
        // Capability New
        capability_new_title: 'New Capability',
        capability_new_description: 'Create a new capability',
        capability_new_desc: 'Register a new capability',
        capability_input_schema_label: 'Input Schema (JSON)',
        capability_output_schema_label: 'Output Schema (JSON)',
        capability_headers_label: 'Headers',
        capability_register_failed: 'Registration failed',
        capability_update_failed: 'Update failed',
        capability_mcp_tool_name: 'Name published as MCP Tool',
        capability_http_method: 'HTTP Method',
        capability_connection_url: 'Connection URL',
        capability_header_params: 'Header Parameters',
        capability_header_params_hint: 'Individual header parameters (added to app common headers)',
        capability_body_params: 'Body Parameters',
        capability_body_params_add: '+ Add Parameter',
        capability_body_params_hint: 'Query parameters or form data',
        capability_body_json_hint: 'Request body in JSON format',
        capability_account_management: 'Connectable Account Management',
        capability_account_management_desc: 'Configure accounts that can connect to this capability',
        capability_enabled_accounts: 'Connectable Accounts',
        capability_disabled_accounts: 'Unset Accounts',
        capability_items_count: 'items',
        capability_url_hint: 'API endpoint URL',
        capability_mcp_template_hint: 'Used for Prompt type',
        capability_description_label: 'Description',
        capability_header_key: 'Key',
        capability_header_value: 'Value',
        capability_param_key: 'Key',
        capability_param_value: 'Value',
        button_add_header: '+ Add Header',
        button_add_param: '+ Add Parameter',
        button_remove: 'Remove',
        capability_name_placeholder: 'e.g., get_user_info',
        capability_url_placeholder: 'e.g., https://api.example.com/users/{id}',
        capability_description_placeholder: 'Enter a description for this capability',
        capability_mcp_template_content_placeholder: 'For Prompt type, enter template content here',
        capability_registered: 'Registered successfully',
        
        // Capability Edit
        capability_edit_title: 'Edit Capability',
        capability_edit_desc: 'Edit capability information',
        capability_json_error: 'Invalid JSON format',
        
        // Account List
        account_list_title: 'Accounts',
        account_list_desc: 'Manage MCP connection accounts',
        account_new_button: 'New Account',
        account_empty: 'No accounts registered',
        account_service: 'Service',
        account_permissions: 'Permissions',
        account_created: 'Created',
        account_delete_confirm: 'Are you sure you want to delete this account?',
        
        // Account Detail
        account_detail_title: 'Account Detail',
        account_detail_desc: 'Account information',
        account_capabilities_title: 'Capabilities available to this account',
        account_edit_info: 'Edit Account Information',
        account_basic_info: 'Basic Information',
        account_name_label: 'Account Name',
        account_notes_label: 'Notes',
        account_service_label: 'Service',
        account_api_key_label: 'API Key',
        account_permissions_label: 'Permissions',
        account_capability_label: 'Capability',
        account_all_capabilities: 'All Capabilities',
        account_permission_type: 'Permission Type',
        account_permission_allow: 'Allow',
        account_permission_deny: 'Deny',
        account_created_at: 'Created At',
        account_updated_at: 'Updated At',
        account_bearer_token: 'Bearer Token',
        account_copy_token: 'Copy',
        account_token_copied: 'Token copied to clipboard',
        account_regenerate_token: 'Regenerate Token',
        account_regenerate_confirm: 'Are you sure you want to regenerate the token? The existing token will be invalidated.',
        account_token_regenerated: 'Token regenerated successfully',
        account_update_success: 'Saved successfully',
        account_no_capabilities: 'No capabilities configured',
        account_unknown_service: 'Unknown Service',
        
        // Account New
        account_new_title: 'New Account',
        account_new_desc: 'Register a new connection account',
        account_notes_placeholder: 'Add notes about this account',
        account_permissions_hint: 'Set access permissions for each capability',
        account_register_failed: 'Registration failed',
        account_update_failed: 'Update failed',
        
        // Common Form
        form_required: 'Required',
        form_optional: 'Optional',
        form_key_placeholder: 'Key (e.g., Authorization)',
        form_value_placeholder: 'Value (e.g., Bearer xxx)',
        form_json_placeholder: 'Enter in JSON format',
        
        // Messages
        error_unknown: 'Unknown error',
        confirm_delete: 'Are you sure you want to delete?',
    }
};

let currentLanguage = 'ja';

/**
 * ブラウザの言語設定を取得（日本語以外は英語）
 */
function detectBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    return browserLang.startsWith('ja') ? 'ja' : 'en';
}

/**
 * サーバーから言語設定を取得
 */
async function getLanguageSetting() {
    try {
        const response = await fetch('/api/settings/language');
        if (!response.ok) {
            throw new Error('Failed to fetch language setting');
        }
        const data = await response.json();
        
        // DBに設定がない場合（初回アクセス）
        if (!data.is_initialized || !data.language) {
            // ブラウザ言語検出を使用（初回のみ）
            const detectedLang = detectBrowserLanguage();
            // DBに保存
            await saveLanguageSetting(detectedLang);
            return detectedLang;
        }
        
        // DBに設定がある場合はそれを使用
        return data.language;
    } catch (error) {
        console.error('Failed to get language setting:', error);
        // エラー時はデフォルトで日本語を使用
        return 'ja';
    }
}

/**
 * 言語設定をサーバーに保存
 */
async function saveLanguageSetting(language) {
    try {
        const response = await fetch('/api/settings/language', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language })
        });
        return response.ok;
    } catch (error) {
        console.error('Failed to save language setting:', error);
        return false;
    }
}

/**
 * 翻訳を取得
 */
function t(key) {
    return translations[currentLanguage]?.[key] || key;
}

/**
 * ページ内の翻訳可能な要素を自動翻訳
 */
function applyTranslations() {
    // data-i18n属性を持つ要素を翻訳
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = t(key);
    });
    
    // data-i18n-placeholder属性を持つ要素のplaceholderを翻訳
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        element.placeholder = t(key);
    });
    
    // data-i18n-title属性を持つ要素のtitleを翻訳
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        element.title = t(key);
    });
}

/**
 * 言語を切り替え
 */
async function switchLanguage(language) {
    if (language !== 'ja' && language !== 'en') {
        language = 'ja';
    }
    
    currentLanguage = language;
    await saveLanguageSetting(language);
    
    // ページをリロード
    window.location.reload();
}

/**
 * 言語スイッチャーを初期化
 */
async function initLanguageSwitcher() {
    // サーバーから言語設定を取得（初回の場合はブラウザ言語検出＆DB保存も実行）
    currentLanguage = await getLanguageSetting();
    
    // 言語スイッチャーのHTMLを作成（セレクトボックス）
    const switcher = document.createElement('div');
    switcher.className = 'language-switcher';
    switcher.innerHTML = `
        <select onchange="switchLanguage(this.value)" class="lang-select">
            <option value="ja" ${currentLanguage === 'ja' ? 'selected' : ''}>🇯🇵 日本語</option>
            <option value="en" ${currentLanguage === 'en' ? 'selected' : ''}>🇺🇸 English</option>
        </select>
    `;
    
    // ヘッダーに追加
    const headerActions = document.querySelector('.header-actions');
    if (headerActions) {
        headerActions.insertBefore(switcher, headerActions.firstChild);
    }
    
    // ページ内の翻訳を適用
    applyTranslations();
}

// 自動初期化は行わない（各画面で明示的に呼び出す）
// これにより、各画面のload関数が実行される前に確実に言語が設定される
