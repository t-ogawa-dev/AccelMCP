# Octopus MCP Proxy テストスイート

[English](README.en.md) | 日本語

## 概要

Octopus MCP Proxy の包括的なテストスイート。ユニットテスト、統合テスト、エンドツーエンドテストをカバーしています。

## テスト構成

```
tests/
├── conftest.py                 # Pytest フィクスチャと設定
├── conftest_playwright.py      # Playwright E2E テスト設定
│
├── unit/                       # ユニットテスト（カテゴリ別に整理）
│   ├── admin/
│   │   └── test_admin_settings.py
│   ├── mcp/
│   │   ├── test_capability_integration.py
│   │   ├── test_capability_testing.py
│   │   ├── test_mcp_protocol.py
│   │   ├── test_mcp_services.py
│   │   ├── test_prompt_and_resource_capability.py
│   │   └── test_stdio_mcp.py
│   ├── security/
│   │   ├── test_permissions.py
│   │   └── test_security.py
│   ├── logging/
│   │   ├── test_connection_logs.py
│   │   └── test_log_search.py
│   ├── templates/
│   │   ├── test_prompt_templates.py
│   │   ├── test_template_import_export.py
│   │   └── test_variables.py
│   ├── ui/
│   │   ├── test_javascript_static.py
│   │   └── test_modal_and_sync.py
│   └── infrastructure/
│       ├── test_database_schema.py
│       ├── test_error_responses.py
│       ├── test_i18n.py
│       └── test_timeout_feature.py
│
├── e2e/                        # エンドツーエンドテスト
│   ├── test_login.py
│   ├── test_dashboard.py
│   ├── accounts/
│   ├── capabilities/
│   ├── mcp_templates/
│   └── services/
│
└── reports/                    # テストレポートとドキュメント
    ├── TEST_COVERAGE.txt
    ├── TEST_SUMMARY.md
    ├── TEST_COMPLETION_REPORT.md
    ├── TEST_FINAL_REPORT.md
    ├── IMPORT_EXPORT_TESTS.md
    ├── PROMPT_RESOURCE_TESTS.md
    └── NEW_TESTS_SUMMARY.txt
```

## テストの実行

### すべてのテスト

```bash
pytest tests/
```

### ユニットテストのみ

```bash
pytest tests/unit/
```

### E2E テストのみ

```bash
pytest tests/e2e/
```

### カテゴリ別のテスト

```bash
# 管理機能のテスト
pytest tests/unit/admin/

# MCP プロトコルとサービスのテスト
pytest tests/unit/mcp/

# セキュリティと権限のテスト
pytest tests/unit/security/

# ロギングのテスト
pytest tests/unit/logging/

# テンプレートと変数のテスト
pytest tests/unit/templates/

# UI のテスト
pytest tests/unit/ui/

# インフラストラクチャのテスト
pytest tests/unit/infrastructure/
```

### 特定のテストファイル

```bash
pytest tests/unit/security/test_security.py
pytest tests/unit/templates/test_variables.py
pytest tests/unit/mcp/test_mcp_services.py
```

### カバレッジ付き

```bash
pytest --cov=app --cov-report=html tests/
```

### 詳細出力

```bash
pytest -v tests/
```

### 特定のテスト関数を実行

```bash
pytest tests/unit/security/test_security.py::TestBruteForceProtection::test_multiple_failed_logins_trigger_lock
```

## テストカテゴリ

### 管理機能テスト (`unit/admin/`)

**test_admin_settings.py**

管理設定機能のテスト:

- 設定の CRUD 操作
- セキュリティ設定（最大試行回数、ロック期間、監査ログ保持期間）
- 言語設定
- 他機能との設定統合

### MCP テスト (`unit/mcp/`)

**test_mcp_protocol.py**

MCP プロトコル実装のテスト:

- MCP リクエスト/レスポンス処理
- Tool 実行
- プロトコル準拠

**test_mcp_services.py**

MCP サービス機能のテスト:

- MCP サービスの CRUD 操作
- サブドメイン vs パスルーティング
- アクセス制御（公開/制限付き）
- MCP サービスとアプリの紐付け
- 有効/無効の切り替え
- **YAML エクスポート/インポート**: アプリと Capability を含む MCP サービスのエクスポート、識別子の衝突処理を含むインポート

**test_capability_integration.py / test_capability_testing.py**

Capability 管理と統合のテスト

**test_prompt_and_resource_capability.py**

プロンプトとリソース Capability のテスト

**test_stdio_mcp.py**

stdio トランスポートプロトコルのテスト

### セキュリティテスト (`unit/security/`)

**test_security.py**

セキュリティ機能のテスト:

- ブルートフォース攻撃対策
- IP ロック/ロック解除
- ログイン失敗の追跡
- ロック期限切れ
- 管理者ログインログ
- 管理者アクションログ（監査証跡）
- セキュリティ API エンドポイント

**test_permissions.py**

ユーザー権限管理のテスト

### ロギングテスト (`unit/logging/`)

**test_connection_logs.py**

MCP 接続ログのテスト

**test_log_search.py**

ログ検索とフィルタリング機能のテスト

### テンプレートテスト (`unit/templates/`)

**test_prompt_templates.py**

プロンプトテンプレート管理のテスト

**test_template_import_export.py**

テンプレートインポート/エクスポート機能のテスト:

- **YAML エクスポート**: 適切なフォーマットでテンプレートを YAML ファイルとしてエクスポート
- **YAML インポート**: バリデーション付きで YAML からテンプレートをインポート
- **Unicode サポート**: YAML 内の日本語と絵文字
- **往復テスト**: エクスポートして再インポートすると同等のデータが生成される
- **エラー処理**: 無効な YAML フォーマットの検出
- **フォーマット品質**: 人間が読みやすい YAML 出力

**test_variables.py**

変数機能のテスト:

- 変数の CRUD 操作
- シークレット変数
- 環境変数の参照
- URL/ヘッダーでの変数置換
- 複数変数の置換
- 未定義変数の処理

### UI テスト (`unit/ui/`)

**test_javascript_static.py**

JavaScript と静的アセット処理のテスト

**test_modal_and_sync.py**

モーダルダイアログと同期処理のテスト

### インフラストラクチャテスト (`unit/infrastructure/`)

**test_database_schema.py**

データベーススキーマとマイグレーションのテスト

**test_error_responses.py**

エラー処理とレスポンスフォーマットのテスト

**test_i18n.py**

国際化（i18n）サポートのテスト

**test_timeout_feature.py**

タイムアウト設定と処理のテスト

## テストカバレッジ

詳細なカバレッジレポートは `reports/TEST_COVERAGE.txt` を参照してください。

### モジュール別の現在のカバレッジ

- **モデル**: ~85%（新モデルを含む: Variable, AdminSettings, LoginLockStatus, AdminLoginLog, AdminActionLog, McpService）
- **API コントローラー**: ~80%（変数、MCP サービス、セキュリティの新エンドポイントを含む）
- **ビュー**: ~80%
- **MCP プロトコル**: ~90%
- **E2E**: ~85%
- **認証とセキュリティ**: ~90%（大幅に改善）

## テストレポート

すべてのテストレポートとドキュメントは `reports/` ディレクトリにあります：

- `TEST_COVERAGE.txt` - 詳細なテストカバレッジレポート
- `TEST_SUMMARY.md` - テスト実装の概要
- `TEST_COMPLETION_REPORT.md` - テスト完了状況
- `TEST_FINAL_REPORT.md` - 最終テストレポート
- `IMPORT_EXPORT_TESTS.md` - インポート/エクスポート機能テストの詳細
- `PROMPT_RESOURCE_TESTS.md` - プロンプトとリソース Capability テストの詳細
- `NEW_TESTS_SUMMARY.txt` - 新規追加テストの概要

## フィクスチャ

### 共通フィクスチャ (conftest.py)

- `app`: Flask アプリケーションインスタンス
- `client`: HTTP リクエスト用テストクライアント
- `auth_client`: 認証済みテストクライアント
- `db`: データベースセッション
- `sample_service`: テスト用サービスインスタンス
- `sample_capability`: テスト用 Capability インスタンス
- `sample_account`: テスト用アカウントインスタンス
- `sample_template`: テスト用テンプレートインスタンス

### E2E フィクスチャ (conftest_playwright.py)

- `page`: Playwright ページインスタンス
- `authenticated_page`: ログイン済みページインスタンス
- `base_url`: アプリケーションのベース URL

## 新しいテストの作成

### ユニットテストの例

```python
def test_create_variable(self, auth_client):
    """変数作成のテスト POST /api/variables"""
    payload = {
        'name': 'TEST_VAR',
        'value': 'test_value',
        'source_type': 'manual',
        'value_type': 'string',
        'is_secret': False
    }
    response = auth_client.post('/api/variables',
                               data=json.dumps(payload),
                               content_type='application/json')

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'TEST_VAR'
```

### E2E テストの例

```python
def test_create_variable(self, page: Page):
    """UI を通して変数を作成するテスト"""
    page.goto(f"{base_url}/variables/new")
    page.fill("#name", "TEST_VAR")
    page.fill("#value", "test_value")
    page.click("button[type=submit]")

    expect(page.locator(".success-message")).to_be_visible()
```

## ベストプラクティス

1. **説明的なテスト名を使用**: テスト名は何をテストしているかを明確に説明する
2. **1テストあたり1アサーション**: 各テストは単一の振る舞いに焦点を絞る
3. **フィクスチャを使用**: 共通のセットアップには pytest フィクスチャを活用
4. **テスト後のクリーンアップ**: テスト間でデータベースをクリーンに保つ
5. **エッジケースをテスト**: エラー条件とエッジケースのテストを含める
6. **Mock external services**: Don't make real API calls in tests
7. **Keep tests fast**: Unit tests should run in milliseconds

## Troubleshooting

### Database Issues

```bash
# Reset test database
docker compose exec db mysql -uroot -prootpassword -e "DROP DATABASE IF EXISTS test_mcpdb; CREATE DATABASE test_mcpdb;"
```

### Playwright Issues

```bash
# Install browsers
python -m playwright install

# Run with headed browser for debugging
pytest tests/e2e/ --headed
```

### Debug Failing Tests

```bash
# Run with pdb debugger
pytest tests/test_security.py --pdb

# Show print statements
pytest tests/test_security.py -s
```

## CI/CD Integration

Tests are automatically run in CI/CD pipeline on:

- Pull requests
- Push to develop/main branches

Configuration: `.github/workflows/test.yml` (if exists)

## Contributing

When adding new features, please:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >80% code coverage
4. Update TEST_COVERAGE.txt
5. Add test documentation if needed
