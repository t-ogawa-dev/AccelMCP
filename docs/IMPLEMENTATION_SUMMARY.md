# 実装完了 - 新しい MCP エンドポイント

## 実装内容

以下の 2 つの主要な MCP エンドポイントを追加しました:

### 1. サブドメインベースの Capabilities 取得・MCP 処理

**エンドポイント**: `<subdomain>.lvh.me:5000/mcp`

- **GET /mcp** - ユーザーが使用可能な Capabilities を取得
- **POST /mcp** - MCP プロトコルリクエストを処理 (tools/list, tools/call)

### 2. Tool 直接実行エンドポイント

**エンドポイント**: `<subdomain>.lvh.me:5000/tools/<tool_id>`

- **POST /tools/<tool_id>** - 特定の Tool を直接実行

## ファイル変更

### 新規作成

- ✅ `MCP_ENDPOINTS.md` - MCP エンドポイントの詳細ドキュメント
- ✅ `test_mcp.py` - テストスクリプト
- ✅ `QUICKSTART.md` - 5 分クイックスタートガイド

### 更新

- ✅ `app.py` - 新しい MCP エンドポイント追加
  - `get_subdomain_from_request()` - サブドメイン抽出関数
  - `authenticate_bearer_token()` - Bearer 認証関数
  - `GET/POST /mcp` - サブドメインベースエンドポイント
  - `POST /tools/<tool_id>` - Tool 直接実行エンドポイント
- ✅ `mcp_handler.py` - 新しいメソッド追加

  - `get_capabilities()` - Capabilities 取得
  - `execute_tool_by_id()` - Tool ID 指定実行

- ✅ `README.md` - エンドポイント使用方法を追加
- ✅ `SETUP.md` - 新しいエンドポイントの設定例を追加

## 主要機能

### サブドメイン指定方法

1. **lvh.me ドメイン** (推奨)

   ```
   http://myservice.lvh.me:5000/mcp
   ```

2. **クエリパラメータ**

   ```
   http://localhost:5000/mcp?subdomain=myservice
   ```

3. **カスタムヘッダー**
   ```
   X-Subdomain: myservice
   ```

### 挙動フロー

#### GET /mcp または POST /mcp (tools/list)

```
1. リクエスト受信
   ↓
2. サブドメインを抽出
   ↓
3. Bearerトークンを検証
   ↓
4. サブドメインからServiceを検索
   ↓
5. ユーザーID + Service IDから権限のあるCapabilityを取得
   ↓
6. Capabilityリストを返却
```

#### POST /tools/<tool_id>

```
1. リクエスト受信
   ↓
2. サブドメインを抽出
   ↓
3. Bearerトークンを検証
   ↓
4. tool_idからCapabilityを検索 (名前 or ID)
   ↓
5. ユーザーの権限を確認
   ↓
6. 権限あり → 実行 (API/MCP中継)
   権限なし → エラーレスポンス
   ↓
7. 結果を返却
```

## 使用例

### Capabilities 取得

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://weather.lvh.me:5000/mcp
```

### Tool 実行 (直接)

```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"city": "Tokyo"}}' \
  http://weather.lvh.me:5000/tools/get_weather
```

### Tool 実行 (MCP プロトコル)

```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
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
  http://weather.lvh.me:5000/mcp
```

## MCP クライアント統合

### Dify

```json
{
  "mcp_servers": {
    "weather": {
      "url": "http://weather.lvh.me:5000/mcp",
      "auth": {
        "type": "bearer",
        "token": "YOUR_TOKEN"
      }
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://weather.lvh.me:5000/mcp",
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

## テスト方法

### 1. クイックテスト

```bash
# QUICKSTART.mdに従って5分でセットアップ
# その後、curlコマンドでテスト
```

### 2. テストスクリプト実行

```bash
# test_mcp.py を編集してトークンとサブドメインを設定
python3 test_mcp.py
```

### 3. 手動テスト

```bash
# 1. Capabilitiesを確認
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://yourservice.lvh.me:5000/mcp

# 2. Toolを実行
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"arguments": {...}}' \
  http://yourservice.lvh.me:5000/tools/TOOL_NAME
```

## エラーハンドリング

実装されたエラーコード:

- `-32700`: Parse error (無効な JSON)
- `-32600`: Invalid Request (サブドメイン未指定)
- `-32601`: Method not found (未対応のメソッド)
- `-32602`: Invalid params (Tool 未発見)
- `-32603`: Internal error (実行エラー)
- `-32000`: Server error (認証・権限エラー)
- `-32001`: Server error (サービス未発見)

すべてのエラーは JSON-RPC 2.0 形式で返却されます。

## 次のステップ

1. **テスト**: `QUICKSTART.md` に従って動作確認
2. **統合**: 実際の MCP クライアント (Dify, Claude) から接続
3. **カスタマイズ**: 独自の API/MCP サーバーを中継
4. **本番化**: HTTPS リバースプロキシの設定

## ドキュメント

- `README.md` - プロジェクト概要
- `QUICKSTART.md` - 5 分クイックスタート
- `SETUP.md` - 詳細セットアップガイド
- `MCP_ENDPOINTS.md` - エンドポイント詳細リファレンス
- `test_mcp.py` - テストスクリプト
