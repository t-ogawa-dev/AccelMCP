# MCP Server with Flask and FastMCP

HTTP/stdio 対応の MCP サーバー。API/MCP 中継機能とユーザー別権限管理を備えた Web 管理画面付き。

## 機能

- **MCP プロトコル対応**: HTTP と stdio の両方をサポート
- **中継機能**: API および MCP サーバーへの中継
- **権限管理**: ユーザーごとの Tool 使用権限制御
- **Web 管理画面**: サービス、Capability、ユーザーの管理
- **Bearer トークン認証**: ユーザー別のトークン発行

## 起動方法

```bash
# Docker Composeで起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# 停止
docker-compose down
```

## アクセス

- Web 管理画面: http://admin.lvh.me:5001/ または http://localhost:5001/
- デフォルト管理者
  - ID: `accel`
  - パスワード: `universe`

**注意**: `admin` サブドメインは管理画面専用です。各サービスのサブドメインとは別に扱われます。

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
  http://myservice.lvh.me:5001/mcp

# または subdomain パラメータを使用
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5001/mcp?subdomain=myservice
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
  http://myservice.lvh.me:5001/tools/get_weather

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
  http://myservice.lvh.me:5001/mcp
```

### MCP クライアント設定

#### HTTP 接続 (Dify, Claude Desktop など)

```json
{
  "mcpServers": {
    "my-service": {
      "url": "http://myservice.lvh.me:5001/mcp",
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
      "url": "http://localhost:5001/mcp/myservice",
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
| `<subdomain>.lvh.me:5001/mcp`             | GET      | ユーザーが使用可能な Capabilities を取得      |
| `<subdomain>.lvh.me:5001/mcp`             | POST     | MCP リクエストを処理 (tools/list, tools/call) |
| `<subdomain>.lvh.me:5001/tools/<tool_id>` | POST     | 特定の Tool を直接実行                        |
| `/mcp/<subdomain>`                        | POST     | Legacy エンドポイント (後方互換性)            |

**注意:** `lvh.me` はローカル開発用のドメインで、常に 127.0.0.1 を指します。本番環境では独自ドメインを使用してください。

## データベース構造

- **users**: ユーザー情報、認証情報
- **services**: 登録サービス (サブドメイン、共通ヘッダー)
- **capabilities**: Tool 定義 (API/MCP、URL、ヘッダー、ボディ)
- **user_permissions**: ユーザー ×Capability の権限マッピング

## 開発

```bash
# ローカルで開発
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
