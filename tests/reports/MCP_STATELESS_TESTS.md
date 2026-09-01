# MCP 2026-07-28 ステートレス対応テスト

テスト対象: MCP 2026-07-28 仕様への後方互換対応

作成日: 2026-09-01

## 背景

MCP 2026-07-28 仕様により、プロトコルがステートレスコアへ移行した。主な変更点は以下のとおり。

- `initialize` ハンドシェイクと `Mcp-Session-Id` ヘッダーが仕様から削除
- 各リクエストが `_meta` フィールドにプロトコルバージョンとケーパビリティを自己記述
- `server/discover` RPC でセッション不要のケーパビリティ検出が可能
- 旧仕様 (`2024-11-05`) クライアントとの後方互換は 12 ヶ月間維持

本レポートは「実装済みか」「テストで正常動作を確認できるか」をまとめる。

## 実装状況

| 対応内容                                    | 実装箇所                                                                           |
| ------------------------------------------- | ---------------------------------------------------------------------------------- |
| ステートレスリクエスト (セッションなし通過) | `app/controllers/mcp_controller.py` セッション検証ロジック (2箇所)                 |
| `server/discover` ルーティング              | `app/services/mcp_handler.py` `handle_mcp_service_request` / `handle_http_request` |
| `server/discover` ハンドラー                | `_handle_server_discover_for_mcp_service` / `_handle_server_discover`              |
| 旧仕様 `initialize` 継続サポート            | 既存 `_handle_initialize_for_mcp_service` / `_handle_initialize`                   |

### セッション検証の変更内容

```
変更前: Mcp-Session-Id が "ない" または "不正" → 400 拒否
変更後: Mcp-Session-Id が存在して "不正"     → 400 拒否
        Mcp-Session-Id が存在しない           → 通過 (新仕様ステートレスクライアント)
```

`server/discover` と `initialize` はセッションチェック対象外。

## テストカバレッジ

ファイル: `tests/unit/mcp/test_mcp_stateless.py`

### TestStatelessClientNoSession (3テスト)

新仕様クライアントが `initialize` なしで直接リクエストできることを確認。

✅ `test_tools_list_without_initialize`

- セッションなし JSON リクエストで `tools/list` が 200 を返す

✅ `test_tools_list_via_sse_without_session`

- `Accept: text/event-stream` (Streamable HTTP) かつ `Mcp-Session-Id` なしで 200 を返す
- 旧実装では 400 になっていた中心的な破壊バグを検証

✅ `test_tools_list_meta_protocol_version`

- `_meta` に `io.modelcontextprotocol/protocolVersion: "2026-07-28"` を含めたリクエストを処理できる

### TestServerDiscover (4テスト)

`server/discover` が仕様どおりのレスポンスを返すことを確認。

✅ `test_server_discover_returns_protocol_versions`

- `result.protocolVersions` に `"2026-07-28"` と `"2024-11-05"` が含まれる

✅ `test_server_discover_returns_capabilities`

- `result.capabilities` にサーバーのケーパビリティ (tools 等) が含まれる

✅ `test_server_discover_returns_no_session_id`

- `result` に `sessionId` が含まれない (セッションを生成しない)

✅ `test_server_discover_via_sse_without_session`

- SSE トランスポートでセッション ID なしの `server/discover` が 200 を返す

### TestLegacyInitializeFlow (2テスト)

旧仕様 (`2024-11-05`) クライアントの `initialize` フローが引き続き動作することを確認。

✅ `test_initialize_returns_session_id`

- `initialize` レスポンスに `sessionId` が含まれる

✅ `test_initialize_protocol_version_backward_compat`

- `initialize` レスポンスの `protocolVersion` が `"2024-11-05"` である

### TestInvalidSessionRejected (1テスト)

不正なセッション ID は依然として拒否されることを確認。

✅ `test_stale_session_id_rejected`

- 存在しない `Mcp-Session-Id` を持つ SSE リクエストが `-32600` で 400 を返す

## テスト結果

**10テスト / 10テスト成功 (100%)**
