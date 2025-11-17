# MCP Server - Testing Guide

## テスト概要

このプロジェクトでは `pytest` を使用してテストを実行します。Rails の RSpec に似た構造で、モデル、API、ビューの各レイヤーをテストします。

## テスト構造

```
tests/
├── __init__.py                 # テストパッケージ初期化
├── conftest.py                 # pytest設定とフィクスチャ
├── conftest_playwright.py      # Playwright設定
├── test_models.py              # モデルのテスト
├── test_api.py                 # API エンドポイントのテスト
├── test_views.py               # ビュー（HTMLページ）のテスト
├── test_integration.py         # 統合テスト
└── e2e/                        # E2Eテスト（Playwright）
    ├── __init__.py
    ├── test_login.py           # ログインページ
    ├── test_dashboard.py       # ダッシュボード
    ├── accounts/
    │   └── test_accounts.py    # アカウント管理
    ├── capabilities/
    │   └── test_capabilities.py # Capabilities管理
    ├── services/
    │   └── test_services.py    # サービス管理
    └── templates/
        └── test_templates.py   # テンプレート管理
```

## セットアップ

### 1. テスト用パッケージのインストール

```bash
pip install -r requirements.txt
```

または個別にインストール:

```bash
pip install pytest pytest-flask pytest-cov pytest-mock pytest-playwright
```

### 2. Playwright ブラウザのインストール（E2E テスト用）

```bash
./setup_playwright.sh
```

または

```bash
python -m playwright install
```

### 3. Docker 環境でのテスト

```bash
docker compose exec web bash
pytest
```

## テストの実行方法

### 全テストを実行

```bash
pytest
```

または

```bash
./run_tests.sh
```

### 特定のファイルのテストを実行

```bash
pytest tests/test_models.py
```

### 特定のクラスのテストを実行

```bash
pytest tests/test_models.py::TestServiceModel
```

### 特定のテストケースを実行

```bash
pytest tests/test_models.py::TestServiceModel::test_create_service
```

### 詳細表示で実行

```bash
pytest -v
```

### カバレッジ付きで実行

```bash
pytest --cov=app --cov-report=term-missing
```

### HTML カバレッジレポート生成

```bash
pytest --cov=app --cov-report=html
```

レポートは `htmlcov/index.html` に生成されます。

## テストの種類

### 1. モデルテスト (`test_models.py`)

データベースモデルの基本的な CRUD 操作とメソッドをテストします。

```python
def test_create_service(self, db):
    """サービスの作成テスト"""
    service = Service(
        subdomain='test',
        name='Test Service',
        service_type='api'
    )
    db.session.add(service)
    db.session.commit()

    assert service.id is not None
```

### 2. API テスト (`test_api.py`)

RESTful API エンドポイントのリクエスト/レスポンスをテストします。

```python
def test_get_services(self, auth_client):
    """サービス一覧取得のテスト"""
    response = auth_client.get('/api/services')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 0
```

### 3. ビューテスト (`test_views.py`)

HTML ページのレンダリングと画面遷移をテストします。

```python
def test_service_list(self, auth_client):
    """サービス一覧画面のテスト"""
    response = auth_client.get('/services')

    assert response.status_code == 200
```

### 4. 統合テスト (`test_integration.py`)

複数のコンポーネントを組み合わせた動作をテストします。

### 5. E2E テスト (`e2e/`) - Playwright

実際のブラウザを使用したエンドツーエンドテスト（Capybara 相当）。

**ファイル構成:**

- `e2e/test_login.py` - ログイン/ログアウト
- `e2e/test_dashboard.py` - ダッシュボード
- `e2e/services/test_services.py` - サービス管理（一覧/新規/編集/削除）
- `e2e/capabilities/test_capabilities.py` - Capabilities 管理（一覧/編集/トグル）
- `e2e/accounts/test_accounts.py` - アカウント管理（一覧/新規/編集/削除）
- `e2e/templates/test_templates.py` - テンプレート管理（一覧/新規/編集/使用）

```python
def test_login_with_valid_credentials(self, page: Page):
    """正しい認証情報でログインできる"""
    page.goto("http://localhost:5001/login")

    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "admin123")
    page.click('button[type="submit"]')

    page.wait_for_url("http://localhost:5001/")
    expect(page).to_have_url("http://localhost:5001/")
```

**E2E テストの実行方法:**

```bash
# サーバーを起動（別ターミナル）
docker compose up

# 全E2Eテスト実行
pytest tests/e2e/

# 特定のページのテスト実行
pytest tests/e2e/test_login.py
pytest tests/e2e/services/test_services.py
pytest tests/e2e/templates/test_templates.py

# マーカーで実行
pytest -m e2e

# ヘッドレスモード無効（ブラウザを表示）
pytest tests/e2e/ --headed

# 特定のブラウザで実行
pytest tests/e2e/ --browser chromium
pytest tests/e2e/ --browser firefox
pytest tests/e2e/ --browser webkit
```

## フィクスチャ

テストで使用できる主なフィクスチャ:

**ユニット/API テスト用:**

- `app` - Flask アプリケーション
- `db` - テスト用データベース
- `client` - テストクライアント（未認証）
- `auth_client` - 認証済みテストクライアント
- `sample_service` - サンプルサービス
- `sample_capability` - サンプル Capability
- `sample_account` - サンプル接続アカウント
- `sample_template` - サンプルテンプレート

**E2E テスト用（Playwright）:**

- `page` - Playwright ページオブジェクト
- `browser` - ブラウザインスタンス
- `context` - ブラウザコンテキスト

使用例:

```python
def test_something(self, auth_client, sample_service):
    """フィクスチャを使用したテスト"""
    response = auth_client.get(f'/services/{sample_service.id}')
    assert response.status_code == 200
```

```python
def test_e2e_example(self, page: Page):
    """E2Eテストの例"""
    page.goto("http://localhost:5001/login")
    page.fill('input[name="username"]', "admin")
    page.click('button[type="submit"]')
```

## テストデータベース

テストは SQLite インメモリデータベースを使用します。各テスト実行後に自動的にクリーンアップされます。

```python
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

## CI/CD 統合

GitHub Actions などの CI 環境でテストを実行する例:

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    python -m playwright install

- name: Run unit tests
  run: |
    pytest tests/ --ignore=tests/test_e2e.py --cov=app --cov-report=xml

- name: Run E2E tests
  run: |
    docker compose up -d
    pytest tests/test_e2e.py
    docker compose down

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## トラブルシューティング

### インポートエラー

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### データベース接続エラー

テスト用のインメモリ DB を使用しているため、MySQL 接続は不要です。

### 認証エラー

`auth_client` フィクスチャを使用してください。これは自動的にログイン済みの状態です。

### E2E テストでサーバーに接続できない

サーバーが起動していることを確認してください:

```bash
docker compose up
```

### Playwright ブラウザがインストールされていない

```bash
python -m playwright install
```

## Playwright デバッグ

### ブラウザを表示して実行

```bash
pytest tests/test_e2e.py --headed
```

### スローモーション実行

`conftest_playwright.py` で `slow_mo` を設定:

```python
"slow_mo": 1000,  # 1秒ずつ遅らせる
```

### スクリーンショット撮影

テスト内で:

```python
page.screenshot(path="debug.png")
```

### トレース記録

```python
context.tracing.start(screenshots=True, snapshots=True)
# テスト実行
context.tracing.stop(path="trace.zip")
```

トレースファイルは Playwright Inspector で確認:

```bash
playwright show-trace trace.zip
```

## ベストプラクティス

1. **テストは独立させる**: 各テストは他のテストに依存しない
2. **AAA パターン**: Arrange（準備）, Act（実行）, Assert（検証）
3. **明確な名前**: テスト名は何をテストしているか明確に
4. **適切なフィクスチャ**: 共通のセットアップはフィクスチャに
5. **カバレッジ目標**: 80%以上を目指す
6. **E2E テストは最小限に**: 実行時間が長いため、重要なユーザーフローのみ

## 参考リンク

- [pytest 公式ドキュメント](https://docs.pytest.org/)
- [pytest-flask](https://pytest-flask.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/en/3.0.x/testing/)
- [Playwright for Python](https://playwright.dev/python/)
- [pytest-playwright](https://github.com/microsoft/playwright-pytest)
