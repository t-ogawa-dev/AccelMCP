# MCP Server with Flask and FastMCP

HTTP/stdio 対応の MCP サーバー。API/MCP 中継機能とユーザー別権限管理を備えた Web 管理画面付き。

## 機能

- **MCP プロトコル対応**: HTTP と stdio の両方をサポート
- **中継機能**: API および MCP サーバーへの中継
- **権限管理**: ユーザーごとの Tool 使用権限制御
- **Web 管理画面**: サービス、Capability、ユーザーの管理
- **Bearer トークン認証**: ユーザー別のトークン発行

## 起動方法

### 開発環境（デフォルト）

```bash
# Docker Composeで起動
docker compose up -d

# ログ確認
docker compose logs -f

# 停止
docker compose down
```

開発環境では Flask 開発サーバーが起動し、コード変更時に自動リロードされます。

### 本番環境

```bash
# Gunicornで起動
FLASK_ENV=production docker compose up -d
```

または `.env` ファイルで設定：

```
FLASK_ENV=production
```

本番環境では Gunicorn が起動し、マルチプロセスで安定した動作を提供します。

### ログレベルの設定

環境変数 `LOG_LEVEL` でログレベルを制御できます：

```bash
# DEBUGレベルで起動（詳細なログを出力）
LOG_LEVEL=DEBUG docker compose up -d

# INFOレベル（デフォルト）
LOG_LEVEL=INFO docker compose up -d
```

利用可能なログレベル：

- `DEBUG`: 詳細なデバッグ情報
- `INFO`: 一般的な情報メッセージ（デフォルト）
- `WARNING`: 警告メッセージ
- `ERROR`: エラーメッセージ
- `CRITICAL`: 重大なエラー

`.env` ファイルで設定することも可能：

```
LOG_LEVEL=DEBUG
```

## アクセス

- Web 管理画面: http://admin.lvh.me:5000/ または http://localhost:5000/
- デフォルト管理者
  - ID: `accel`
  - パスワード: `universe`

**⚠️ セキュリティ警告**

- **本番環境では必ず認証情報を変更してください**
- 環境変数 `ADMIN_USERNAME` と `ADMIN_PASSWORD` で上書き可能です
- デフォルト認証情報はデモ・検証用です（Oracle の scott/tiger のような位置づけ）

**環境変数での認証情報変更：**

```bash
# docker-compose.yml または .env
environment:
  ADMIN_USERNAME: your_secure_username
  ADMIN_PASSWORD: your_secure_password
```

**注意**: `admin` サブドメインは管理画面専用です。各サービスのサブドメインとは別に扱われます。

## セキュリティ機能

### ブルートフォース攻撃対策

管理画面ログインは IP アドレスベースのレート制限機能を備えています：

- **デフォルト設定**: 5 回の失敗で 30 分間ロック
- **ログ記録**: 全ログイン試行（成功/失敗）を記録
- **手動ロック解除**: 管理画面から IP アドレスのロックを解除可能

### 監査ログ機能

すべての管理者操作が自動的に記録されます：

- **ログイン履歴**: ユーザー名、IP アドレス、成功/失敗、タイムスタンプ
- **CRUD 操作履歴**: MCP サービス、アプリ、Capability、アカウント、権限の作成・更新・削除
- **変更差分**: 操作前後の値を JSON 形式で記録
- **CSV エクスポート**: 監査レポート用に CSV 出力可能

**監査ログ API:**

- `GET /api/admin/login-logs` - ログイン履歴取得
- `GET /api/admin/login-logs/export` - ログイン履歴 CSV 出力
- `GET /api/admin/action-logs` - 操作履歴取得
- `GET /api/admin/action-logs/export` - 操作履歴 CSV 出力
- `POST /api/admin/unlock-account` - IP ロック解除
- `GET /api/admin/locked-ips` - ロック中 IP 一覧

### セキュリティ設定

AdminSettings で以下の設定をカスタマイズ可能：

- `login_max_attempts`: ログイン試行上限（デフォルト: 5）
- `login_lock_duration_minutes`: ロック時間（デフォルト: 30 分）
- `audit_log_retention_days`: 監査ログ保持期間（デフォルト: 365 日）

## 管理画面構成

### ログイン画面

- 管理者認証

### サービス管理

- サービス一覧表示
- サービス新規登録 (サブドメイン、共通ヘッダー設定)
- サービス詳細/編集
- Capability 管理

### Capability 管理

- Capability 一覧
- Capability 登録 (API/MCP 選択、URL、ヘッダー、ボディ設定)
- Capability 編集/削除

### ユーザー管理

- ユーザー一覧
- ユーザー登録 (ログイン ID、パスワード)
- ユーザー詳細 (Bearer トークン表示)
- ユーザー情報編集/削除

## MCP クライアント接続

### サブドメインベースのアクセス (推奨)

#### 1. Capabilities 取得 (GET リクエスト)

```bash
# lvh.me ドメインを使用 (ローカル開発用)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://myservice.lvh.me:5000/mcp

# または subdomain パラメータを使用
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/mcp?subdomain=myservice
```

**レスポンス例:**

```json
{
  "capabilities": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather information",
        "inputSchema": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "Parameter: city"
            }
          }
        }
      }
    ]
  },
  "serverInfo": {
    "name": "Weather Service",
    "version": "1.0.0"
  }
}
```

#### 2. Tool 実行 (POST リクエスト)

```bash
# Tool を直接実行
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"city": "Tokyo"}}' \
  http://myservice.lvh.me:5000/tools/get_weather

# または MCP プロトコルで実行
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {"city": "Tokyo"}
    }
  }' \
  http://myservice.lvh.me:5000/mcp
```

### MCP クライアント設定

#### HTTP 接続 (Dify, Claude Desktop など)

```json
{
  "mcpServers": {
    "my-service": {
      "url": "http://myservice.lvh.me:5000/mcp",
      "transport": {
        "type": "http"
      },
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

#### Legacy エンドポイント (後方互換性)

```json
{
  "mcpServers": {
    "my-service": {
      "url": "http://localhost:5000/mcp/myservice",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

### stdio 接続

```json
{
  "mcpServers": {
    "my-service": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "mcp_server",
        "python",
        "stdio_server.py",
        "myservice",
        "YOUR_TOKEN"
      ]
    }
  }
}
```

## エンドポイント一覧

### MCP エンドポイント

| エンドポイント                            | メソッド | 説明                                          |
| ----------------------------------------- | -------- | --------------------------------------------- |
| `<subdomain>.lvh.me:5000/mcp`             | GET      | ユーザーが使用可能な Capabilities を取得      |
| `<subdomain>.lvh.me:5000/mcp`             | POST     | MCP リクエストを処理 (tools/list, tools/call) |
| `<subdomain>.lvh.me:5000/tools/<tool_id>` | POST     | 特定の Tool を直接実行                        |
| `/mcp/<subdomain>`                        | POST     | Legacy エンドポイント (後方互換性)            |

**注意:** `lvh.me` はローカル開発用のドメインで、常に 127.0.0.1 を指します。本番環境では独自ドメインを使用してください。

## データベース構造

- **users**: ユーザー情報、認証情報
- **services**: 登録サービス (サブドメイン、共通ヘッダー)
- **capabilities**: Tool 定義 (API/MCP、URL、ヘッダー、ボディ)
- **user_permissions**: ユーザー ×Capability の権限マッピング
- **mcp_connection_logs**: MCP 接続ログ（監査用）

## 接続ログ

### 標準出力への JSON 構造化ログ

AccelMCP は、すべての MCP 接続ログを標準出力（stdout）に JSON 形式で出力します。これにより、任意のコンテナログ収集システムで自動的にログを集約できます。

**対応プラットフォーム：**

- **AWS ECS/Fargate** → CloudWatch Logs
- **Google Cloud Run** → Cloud Logging
- **Azure Container Apps** → Azure Monitor
- **Kubernetes** → kubelet → Fluentd/Fluent Bit → 任意のバックエンド
- **Heroku** → Logplex
- その他、Docker コンテナをサポートするすべてのプラットフォーム

**ログ形式例：**

```json
{
  "timestamp": "2026-01-08T12:34:56.789Z",
  "log_type": "mcp_connection",
  "level": "INFO",
  "mcp_method": "tools/call",
  "mcp_service_id": 7,
  "mcp_service_name": "OpenAI Service",
  "app_id": 43,
  "app_name": "ChatGPT API",
  "capability_id": 215,
  "capability_name": "generate_text",
  "tool_name": "generate_text",
  "account_id": null,
  "account_name": null,
  "status_code": 200,
  "is_success": true,
  "duration_ms": 1234,
  "ip_address": "192.168.1.1",
  "user_agent": "Claude/1.0",
  "access_control": "public",
  "request_id": "abc123",
  "error_code": null,
  "error_message": null,
  "request_body": "{\"prompt\":\"Hello\"}",
  "response_body": "{\"text\":\"Hi there!\"}"
}
```

### 環境変数設定

```bash
# 標準出力ログの有効/無効（デフォルト: true）
MCP_LOG_STDOUT=true
```

### ログ無効化

開発環境でログ出力を無効にする場合：

```bash
MCP_LOG_STDOUT=false docker compose up
```

### クラウドプラットフォームでの活用

**AWS ECS/Fargate:**

```json
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/accel-mcp",
      "awslogs-region": "ap-northeast-1",
      "awslogs-stream-prefix": "mcp"
    }
  }
}
```

CloudWatch Insights で検索：

```
fields @timestamp, mcp_method, tool_name, duration_ms, is_success
| filter log_type = "mcp_connection"
| filter is_success = false
| sort @timestamp desc
```

**Google Cloud Run:**

自動的に Cloud Logging に送信され、`jsonPayload`フィールドでフィルタリング可能：

```
jsonPayload.log_type="mcp_connection"
jsonPayload.is_success=false
```

**Kubernetes (Fluent Bit):**

```yaml
[FILTER]
    Name parser
    Match *
    Key_Name log
    Parser json

[FILTER]
    Name modify
    Match *
    Condition Key_value_matches log_type mcp_connection
    Add k8s_label_app accel-mcp
```

## 開発

```bash
# ローカルで開発
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
