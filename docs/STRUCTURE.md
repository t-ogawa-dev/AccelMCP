[English](en/STRUCTURE.en.md) | 日本語

# MVC ディレクトリ構造

このプロジェクトは MVC（Model-View-Controller）パターンに従って構成されています。

## ディレクトリ構造

```
AccelMCP/
├── app/                          # メインアプリケーションパッケージ
│   ├── __init__.py              # アプリケーションファクトリ
│   ├── controllers/             # コントローラー層
│   │   ├── __init__.py
│   │   ├── auth_controller.py   # 認証関連 (ログイン/ログアウト)
│   │   ├── admin_controller.py  # 管理画面ルート
│   │   ├── api_controller.py    # RESTful API エンドポイント
│   │   └── mcp_controller.py    # MCPプロトコルエンドポイント
│   ├── models/                  # モデル層
│   │   ├── __init__.py
│   │   └── models.py            # DBモデル (McpService, Service, Capability, 等)
│   ├── views/                   # ビュー層
│   │   ├── __init__.py
│   │   └── templates/           # HTMLテンプレート
│   ├── assets/                  # 静的ファイル (CSS, JS)
│   ├── services/                # ビジネスロジック層
│   │   ├── __init__.py
│   │   ├── mcp_handler.py      # MCPリクエスト処理・中継
│   │   ├── mcp_logger.py       # MCP接続ログの構造化出力
│   │   ├── mcp_discovery.py    # MCPサービスのタイプ検出
│   │   ├── audit_logger.py     # 監査ログ・アクセスログ
│   │   ├── template_sync.py    # ビルトインテンプレートの同期
│   │   └── variable_replacer.py # 変数展開
│   ├── config/                  # 設定ファイル
│   │   ├── __init__.py
│   │   └── config.py            # アプリケーション設定
│   └── utils/                   # ユーティリティ
│       └── i18n.py              # 国際化ヘルパー
├── db/                          # データベース管理
│   ├── migrate.py              # マイグレーション管理スクリプト
│   ├── migrations/             # Alembicマイグレーション
│   └── seeds/                  # 初期データシード
├── data/
│   └── builtin_templates/      # ビルトインテンプレート定義
├── tests/                       # テストスイート
│   ├── unit/                   # ユニットテスト
│   └── e2e/                    # E2Eテスト (Playwright)
├── docs/                        # ドキュメント
├── run.py                       # アプリケーション起動スクリプト
├── run_check.sh                 # コード品質チェックスクリプト
├── run_format.sh               # コードフォーマットスクリプト
├── run_tests.sh                # テスト実行スクリプト
├── setup_playwright.sh         # Playwright初期セットアップ
├── requirements.txt            # Python依存関係
├── pyproject.toml              # Ruff/mypy設定
├── Dockerfile                  # Dockerイメージ定義
└── compose.yaml                # Docker Compose設定
```

## 各層の役割

### Controllers (コントローラー)

リクエストを受け取り、適切なサービスやモデルを呼び出し、レスポンスを返す。

- **auth_controller.py**: 認証処理 (ログイン/ログアウト)
- **admin_controller.py**: 管理画面のルーティング
- **api_controller.py**: RESTful API (CRUD 操作)
- **mcp_controller.py**: MCP プロトコルのエンドポイント

### Models (モデル)

データベースとのやり取りを担当。データ構造を定義。

- **models.py**:
  - `McpService` - MCPサービス定義
  - `Service` - アプリ（appsテーブルにマッピング）
  - `Capability` - Tool 定義
  - `ConnectionAccount` - 接続アカウント（ユーザー）
  - `AccountPermission` - アカウント権限
  - `McpConnectionLog` - MCP接続ログ
  - `McpServiceTemplate` / `McpCapabilityTemplate` - テンプレート

### Views (ビュー)

ユーザーに表示される画面。HTML テンプレートと CSS。

- **templates/**: Jinja2 テンプレート
- **assets/**: CSS、JavaScript、画像などの静的ファイル

### Services (サービス)

ビジネスロジックを実装。コントローラーとモデルの間の処理。

- **mcp_handler.py**: MCPリクエスト処理、API/MCP中継、権限チェック
- **mcp_logger.py**: MCP接続ログの構造化JSON出力
- **mcp_discovery.py**: MCPサービスのタイプ自動検出
- **audit_logger.py**: 管理操作監査ログ、ログイン履歴
- **template_sync.py**: ビルトインテンプレートのGitHub同期
- **variable_replacer.py**: URL・ヘッダー内の変数展開

### Config (設定)

アプリケーション設定を管理。

- **config.py**:
  - データベース接続
  - シークレットキー
  - デバッグモード等

## 起動方法

### ローカル開発

```bash
python run.py
```

### Docker

```bash
docker compose up -d
```

## インポートパス

新しい構造では、以下のようにインポートします:

```python
# モデル
from app.models.models import db, McpService, Service, Capability, ConnectionAccount, AccountPermission

# サービス
from app.services.mcp_handler import MCPHandler

# 設定
from app.config.config import Config
```

## 旧構造からの変更点

### 変更内容

- `app.py` → 分割: `app/__init__.py` + `app/controllers/*`
- `models.py` → `app/models/models.py`
- `mcp_handler.py` → `app/services/mcp_handler.py`
- `templates/` → `app/views/templates/`
- `static/` → `app/assets/`
- DB管理: SQLファイル → Flask-Migrate (Alembic) (`db/migrations/`)

## 利点

1. **関心の分離**: 各層が明確に分離され、保守性が向上
2. **スケーラビリティ**: 機能追加時に適切な場所に配置できる
3. **テストしやすさ**: 各層を独立してテスト可能
4. **可読性**: ファイルの役割が明確
5. **再利用性**: サービス層のロジックを複数のコントローラーから利用可能

## 開発ガイドライン

### 新機能追加時

1. **新しいエンドポイント追加**
   - 管理画面: `app/controllers/admin_controller.py`
   - API: `app/controllers/api_controller.py`
   - MCP: `app/controllers/mcp_controller.py`

2. **新しいモデル追加**
   - `app/models/models.py` に追加

3. **新しいビジネスロジック追加**
   - `app/services/` に新しいサービスクラスを作成

4. **新しい設定追加**
   - `app/config/config.py` に追加

### コーディング規約

- **Controllers**: Blueprint を使用
- **Models**: SQLAlchemy ORM
- **Services**: クラスベースで実装
- **命名規則**:
  - ファイル: snake_case (例: `auth_controller.py`)
  - クラス: PascalCase (例: `MCPHandler`)
  - 関数: snake_case (例: `get_capabilities`)

## トラブルシューティング

### インポートエラー

```python
# 正しい
from app.models.models import User

# 間違い
from models import User
```

### テンプレートが見つからない

- `app/__init__.py` で `template_folder='views/templates'` を確認
- パスは `app/` からの相対パス

### 静的ファイルが読み込めない

- `app/__init__.py` で `static_folder='assets'` を確認
- HTML では `/assets/style.css` として参照
