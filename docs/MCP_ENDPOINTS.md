# MCP エンドポイント詳細ガイド

このドキュメントでは、MCP サーバーの各エンドポイントの詳細な使用方法を説明します。

## 概要

この MCP サーバーは 3 つの主要なエンドポイントを提供します:

1. **GET /mcp** - Capabilities 一覧取得
2. **POST /mcp** - MCP プロトコルリクエスト処理
3. **POST /tools/<tool_id>** - 直接 Tool 実行

すべてのエンドポイントはサブドメインベースのルーティングをサポートしています。
管理画面は `http://admin.lvh.me:5001/` でアクセス可能です。

## サブドメインの指定方法

### 方法 1: lvh.me ドメイン (推奨)

`lvh.me` は常に 127.0.0.1 を指すため、ローカル開発で便利です。

```
http://<subdomain>.lvh.me:5001/mcp
```

**例:**

- `http://weather.lvh.me:5001/mcp` - weather サービスの MCP エンドポイント
- `http://myapi.lvh.me:5001/mcp` - myapi サービスの MCP エンドポイント
- `http://admin.lvh.me:5001/` - 管理画面（サブドメイン admin は管理画面専用）

### 方法 2: クエリパラメータ

```
http://localhost:5001/mcp?subdomain=<subdomain>
```

### 方法 3: カスタムヘッダー

```bash
curl -H "X-Subdomain: myservice" http://localhost:5001/mcp
```

## 認証

すべてのリクエストには `Authorization` ヘッダーが必要です:

```
Authorization: Bearer <USER_BEARER_TOKEN>
```

ユーザーの Bearer トークンは、Web 管理画面のユーザー詳細ページで確認できます。

---

## 1. GET /mcp - Capabilities 取得

ユーザーが使用可能な Tool の一覧を取得します。

### リクエスト

```bash
curl -H "Authorization: Bearer abc123..." \
  http://myservice.lvh.me:5001/mcp
```

### レスポンス

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
              "description": "Parameter: city",
              "default": "Tokyo"
            },
            "units": {
              "type": "string",
              "description": "Parameter: units",
              "default": "metric"
            }
          },
          "required": []
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

### 挙動

1. サブドメインからサービスを特定
2. Bearer トークンからユーザーを特定
3. ユーザーが権限を持つ Capability のみを返却
4. 各 Capability の InputSchema は、登録された Body パラメータから自動生成

---

## 2. POST /mcp - MCP プロトコルリクエスト

標準的な MCP プロトコルに従ってリクエストを処理します。

### 対応メソッド

- `tools/list` - Tool 一覧取得 (GET /mcp と同等)
- `tools/call` - Tool 実行

### 2.1 tools/list

#### リクエスト

```bash
curl -X POST \
  -H "Authorization: Bearer abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }' \
  http://myservice.lvh.me:5001/mcp
```

#### レスポンス

```json
{
  "jsonrpc": "2.0",
  "result": {
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
  }
}
```

### 2.2 tools/call

#### リクエスト

```bash
curl -X POST \
  -H "Authorization: Bearer abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {
        "city": "Tokyo"
      }
    }
  }' \
  http://myservice.lvh.me:5001/mcp
```

#### レスポンス (成功時)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"data\": {\"temperature\": 25, \"condition\": \"sunny\"}}"
      }
    ]
  }
}
```

#### レスポンス (権限エラー)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": {
    "code": -32603,
    "message": "Permission denied for tool: get_weather"
  }
}
```

---

## 3. POST /tools/<tool_id> - 直接 Tool 実行

Tool ID を直接指定して実行するシンプルなエンドポイント。

### リクエスト

```bash
curl -X POST \
  -H "Authorization: Bearer abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "city": "Tokyo"
    }
  }' \
  http://myservice.lvh.me:5001/tools/get_weather
```

### Tool ID の指定方法

- **Capability 名** (推奨): `get_weather`
- **Capability ID**: `1`, `2`, `3` など

### レスポンス (成功時)

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": true, \"data\": {\"temperature\": 25}}"
    }
  ],
  "isError": false
}
```

### レスポンス (権限エラー)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Permission denied for tool: get_weather"
  }
}
```

### レスポンス (Tool 未発見)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Tool not found: invalid_tool"
  }
}
```

---

## エラーコード一覧

| コード | 説明                                  |
| ------ | ------------------------------------- |
| -32700 | Parse error - 無効な JSON             |
| -32600 | Invalid Request - サブドメイン未指定  |
| -32601 | Method not found - 未対応のメソッド   |
| -32602 | Invalid params - Tool が見つからない  |
| -32603 | Internal error - 実行エラー           |
| -32000 | Server error - 認証エラー、権限エラー |
| -32001 | Server error - サービス未発見         |

---

## 使用例

### 例 1: Dify での設定

```json
{
  "mcp_servers": {
    "weather_service": {
      "url": "http://weather.lvh.me:5001/mcp",
      "auth": {
        "type": "bearer",
        "token": "YOUR_BEARER_TOKEN"
      }
    }
  }
}
```

### 例 2: Claude Desktop での設定

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://weather.lvh.me:5001/mcp",
      "transport": {
        "type": "http"
      },
      "headers": {
        "Authorization": "Bearer YOUR_BEARER_TOKEN"
      }
    }
  }
}
```

### 例 3: Python スクリプトでの利用

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_BEARER_TOKEN',
    'Content-Type': 'application/json'
}

# Capabilities取得
response = requests.get(
    'http://myservice.lvh.me:5001/mcp',
    headers=headers
)
capabilities = response.json()
print(capabilities)

# Tool実行
response = requests.post(
    'http://myservice.lvh.me:5001/tools/get_weather',
    headers=headers,
    json={'arguments': {'city': 'Tokyo'}}
)
result = response.json()
print(result)
```

### 例 4: cURL での完全なワークフロー

```bash
# 1. Capabilitiesを取得
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://myservice.lvh.me:5001/mcp

# 2. 特定のToolを実行
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"city": "Tokyo"}}' \
  http://myservice.lvh.me:5001/tools/get_weather

# 3. MCPプロトコルでToolを実行
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

---

## 実装の流れ

### GET /mcp または POST /mcp (tools/list)

```
1. リクエスト受信
   ↓
2. サブドメインを抽出 (lvh.me, クエリパラメータ, ヘッダー)
   ↓
3. Bearerトークンを検証
   ↓
4. サブドメインからServiceを検索
   ↓
5. ユーザーIDとService IDから権限のあるCapabilityを取得
   ↓
6. Capabilityリストを整形して返却
```

### POST /tools/<tool_id>

```
1. リクエスト受信
   ↓
2. サブドメインを抽出
   ↓
3. Bearerトークンを検証
   ↓
4. サブドメインからServiceを検索
   ↓
5. tool_idからCapabilityを検索 (名前またはID)
   ↓
6. ユーザーの権限を確認
   ↓
7. 権限あり → Capability実行 (API/MCP中継)
   権限なし → エラーレスポンス
   ↓
8. 結果を返却
```

### POST /mcp (tools/call)

```
1. リクエスト受信
   ↓
2. サブドメインを抽出
   ↓
3. Bearerトークンを検証
   ↓
4. サブドメインからServiceを検索
   ↓
5. params.nameからCapabilityを検索
   ↓
6. ユーザーの権限を確認
   ↓
7. 権限あり → Capability実行
   権限なし → JSON-RPCエラーレスポンス
   ↓
8. JSON-RPC形式で結果を返却
```

---

## トラブルシューティング

### サブドメインが認識されない

**問題:** lvh.me でアクセスしてもサブドメインが認識されない

**解決策:**

1. DNS 設定を確認 (`ping myservice.lvh.me` が 127.0.0.1 を返すか)
2. 代わりにクエリパラメータを使用: `?subdomain=myservice`
3. ポート番号を含める: `http://myservice.lvh.me:5001/mcp`

### 認証エラー

**問題:** `Invalid bearer token` エラー

**解決策:**

1. Bearer トークンを確認 (Web 管理画面 > ユーザー詳細)
2. `Authorization: Bearer ` の形式を確認 (スペース含む)
3. トークンを再発行

### 権限エラー

**問題:** `Permission denied for tool: xxx`

**解決策:**

1. Web 管理画面でユーザーの権限を確認
2. ユーザー詳細 > 権限管理 で該当 Capability を追加

### Tool 未発見エラー

**問題:** `Tool not found: xxx`

**解決策:**

1. Capability が正しく登録されているか確認
2. Tool 名のスペルミスがないか確認
3. 正しいサービス(サブドメイン)にアクセスしているか確認
