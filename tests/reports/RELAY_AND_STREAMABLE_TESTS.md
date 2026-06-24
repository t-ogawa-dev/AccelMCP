# Hub/Relay & Streamable HTTP Tests

テスト対象: AccelMCP の中核であるハブ/中継機能と Streamable HTTP トランスポート

作成日: 2026-06-24
更新日: 2026-06-24 (Streamable HTTP クライアント改修 + 実サーバー連結結合テストを追加)

## 背景

AccelMCP は以下の3トポロジーで MCP/API のハブを提供することを目的としている。

```
1. MCPクライアント(Agent/DIFY) ── AccelMCP ── APIサーバ        (API中継)
2. MCPクライアント(Agent/DIFY) ── AccelMCP ── MCPサーバ        (MCP中継)
3. MCPクライアント(Agent/DIFY) ── AccelMCP ── AccelMCP ── MCPサーバ (連結 / daisy-chain)
```

加えて Streamable HTTP (SSE) トランスポートにも対応している。

本レポートは「これらが実装済みか」「テストで正常動作を確認できるか」を検証し、
不足していたテストを新規作成した結果をまとめる。

## 実装状況の確認結果

すべて実装済みであることをコードレビューで確認した。

| 機能 | 実装箇所 |
| --- | --- |
| API中継 | `app/services/mcp_handler.py` `_execute_api_call` (L1046-) |
| HTTP MCP中継 | `app/services/mcp_handler.py` `_execute_mcp_call` httpパス (L1196-) |
| stdio MCP中継 | `app/services/mcp_handler.py` `_execute_stdio_mcp_call` (L1284-) |
| デイジーチェーン(連結) | `_execute_mcp_call` 内 `X-AccelMCP-Depth` 深度制御 (L1222-1231, max_depth=10) |
| Streamable HTTP | `app/controllers/mcp_controller.py` `_is_streamable_http_request` / `_build_sse_response` / セッション管理 (L86-133, 各エンドポイント) |

## 既存テストカバレッジの調査結果

| 機能 | 調査前の状況 |
| --- | --- |
| API中継 | △ `test_capability_testing.py`(test実行API経由)と `test_mcp_protocol.py` にあるが、後者は httpbin.org への実通信依存で脆い |
| HTTP MCP中継 | ❌ 専用テストなし |
| stdio MCP中継 | ✅ `test_stdio_mcp.py` でモックテスト済み |
| デイジーチェーン | ❌ 完全に未テスト (`X-AccelMCP-Depth` を検証するテストが皆無) |
| Streamable HTTP (Admin MCP `/admin/mcp`) | ✅ `test_admin_mcp.py` で手厚くカバー |
| Streamable HTTP (メイン `/mcp`, `/<id>/mcp`) | ❌ `sessionId` 存在確認1件のみ。SSEレスポンス本体・セッション検証・DELETE終了が未テスト |

→ HTTP MCP中継・デイジーチェーン・メインエンドポイントの Streamable HTTP が不足。

## 実装改修(2026-06-24): Streamable HTTP クライアント対応

当初の調査で「全区間 streamable http の連結」を検証する過程で、中継のクライアント側
(`_execute_mcp_call`) に以下のギャップを発見し、改修した。

- **改修前**: 上流へのリクエストに `Accept` を付けず(httpx既定の `*/*`)、レスポンスは
  `response.json()` で固定パースしていた。このため、
  - 上流が SSE (`text/event-stream`) でしか応答しない純正 Streamable HTTP サーバー
    (別の AccelMCP を含む)に接続すると、レスポンスをパースできず中継が壊れる。
  - また `Mcp-Session-Id` が事前指定された場合に `timeout_seconds` 未定義で `NameError`
    になる潜在バグもあった。
- **改修後** (`app/services/mcp_handler.py`):
  - 中継リクエストに `Accept: application/json, text/event-stream` を付与し、AccelMCP が
    Streamable HTTP **クライアント**として振る舞うようにした。
  - 新ヘルパー `_parse_mcp_http_response()` を追加し、上流が JSON でも SSE でも
    正しくパースできるようにした(SSE は `data:` イベントの JSON を取り出す)。
  - `timeout_seconds` の定義位置を修正(NameError バグ解消)。

これにより `Agent ─ AccelMCP ─ AccelMCP ─ MCPサービス` を**全区間 Streamable HTTP**で
連結できるようになった。

## 新規テストファイル (1) ユニット

`tests/unit/mcp/test_relay_and_streamable.py` (17 tests, 全件成功)

外部 HTTP 通信 (`httpx.post`) はすべてモックしており、実在の上流サーバーに依存しない
hermetic なテストになっている。

### `TestApiRelay` (2 tests) — API中継

- `test_api_relay_tool_call_success` — tools/call が API-typeのcapabilityで上流APIへ中継され、
  返ってきたデータが MCP content に包まれて返ること。上流URLが正しいことも確認
- `test_api_relay_merges_common_and_capability_headers` — アプリ共通ヘッダーと
  Capability個別ヘッダーの両方が上流APIに転送されること

### `TestMcpHttpRelay` (5 tests) — HTTP MCP中継

- `test_mcp_relay_tool_call_success` — mcp_tool capability の tools/call が、
  上流MCPサーバへの initialize(セッション確立) → tools/call の2段中継として実行され、
  上流レスポンスがそのまま返ること
- `test_mcp_relay_forwards_tool_name_and_arguments` — 中継先へ渡す tools/call ボディが
  capability名・呼び出し側argumentsを正しく使っていること
- `test_mcp_relay_forwards_common_headers` — アプリ共通ヘッダー(上流認証など)が
  上流MCPサーバに転送されること
- `test_mcp_relay_advertises_streamable_http_accept` — AccelMCP が Streamable HTTP
  クライアントとして `Accept: text/event-stream` を上流へ送ること(改修分)
- `test_mcp_relay_parses_upstream_sse_response` — 上流が SSE で応答した場合でも
  `data:` イベントを正しくパースして中継できること(改修分。`.json()` 依存だと壊れる)

### `TestDaisyChain` (3 tests) — 連結 / デイジーチェーン

- `test_depth_header_is_incremented_and_propagated` — 受信した `X-AccelMCP-Depth: 3` が
  +1 されて `4` として上流へ伝播すること(チェーンの次段が計数を継続できる)
- `test_default_depth_starts_at_one` — 深度ヘッダーが無い場合、転送時の深度は 1 から始まること
- `test_max_depth_exceeded_aborts_without_upstream_call` — 最大深度(10)で中継が拒否され、
  上流HTTP呼び出しが一切発生しないこと(ループ/暴走チェーン防止)

### `TestStreamableHttp` (6 tests) — メイン /mcp の Streamable HTTP

- `test_initialize_returns_sse_with_session` — `Accept: text/event-stream` の initialize が
  SSEレスポンス・`Mcp-Session-Id` ヘッダー・payload内 sessionId を返すこと
- `test_subsequent_request_requires_valid_session` — initialize以外のSSEリクエストで
  有効なセッションIDが無い場合 400(-32600) で拒否されること
- `test_session_roundtrip_allows_followup_request` — initialize でセッション確立後、
  そのセッションID付きの後続SSEリクエストが成功しSSEで返ること
- `test_get_with_sse_accept_returns_405` — `Accept: text/event-stream` の GET
  (サーバープッシュ要求)は非対応で 405 を返すこと
- `test_delete_terminates_session` — 有効なセッションIDの DELETE が 200 で終了し、
  再度の DELETE は 404 になること
- `test_plain_json_still_works_without_sse` — 後方互換: 通常のJSON POST(SSE非要求)は
  プレーンJSONで返ること

### `TestPathRoutingRelay` (1 test) — パスルーティング経由の中継

- `test_api_relay_over_path_routing` — パスベースエンドポイント `/<identifier>/mcp` 経由でも
  API中継が機能すること

## 新規テストファイル (2) 結合 (実サーバー)

`tests/integration/test_streamable_chain.py` (4 tests, `@pytest.mark.integration`, 全件成功)

ローカルに実サーバーを3つ起動して、製品目標そのままのトポロジーを end-to-end で検証する。

```
Agent (httpx, Accept: text/event-stream)
  --SSE--> AccelMCP-A  (/a/mcp, MCP中継)
    --SSE--> AccelMCP-B  (/b/mcp, MCP中継)
      --SSE--> 末端MCPサービス (最小 Streamable HTTP MCP サーバー)
```

- 2つの AccelMCP はそれぞれ独立した一時SQLiteファイルDBで起動(= 実インスタンス2つの連結)
- 各ホップへ `Accept: text/event-stream` で接続し、全区間が SSE になることを確認
- 末端サーバーは受信した `X-AccelMCP-Depth` をエコーし、多段中継での深度伝播を実測

テスト一覧:

- `test_agent_streamable_initialize_against_first_hop` — Agent が先頭ホップAと
  Streamable HTTP セッションを確立できる
- `test_full_chain_tools_call_over_streamable_http` — Agent→A→B→末端の全段SSEで
  tools/call が末端まで届き、エコーされた結果が末端まで戻ること
- `test_daisy_chain_depth_increments_across_hops` — 末端が受信する深度が `2`
  (A→B で1、B→末端 で2)になり、連結の深度伝播が実環境で機能すること
- `test_second_hop_directly_also_serves_streamable_http` — 中段の AccelMCP-B も
  単独で Streamable HTTP を提供すること

## テスト実行

```bash
# ユニット(本機能)
python -m pytest tests/unit/mcp/test_relay_and_streamable.py -v

# 結合(実サーバー連結)
python -m pytest tests/integration/test_streamable_chain.py -v
# または整合マーカーで
python -m pytest -m integration

# ユニット全体
python -m pytest tests/unit/
```

## テスト結果

```
tests/unit/mcp/test_relay_and_streamable.py:        17 passed
tests/integration/test_streamable_chain.py:          4 passed
tests/unit/ (全体):                                 343 passed  ※既存326 + 新規17、回帰なし
```

## 補足

- stdio MCP中継は既存の `tests/unit/mcp/test_stdio_mcp.py` でカバー済みのため本ファイルでは扱わない
  (デイジーチェーンの深度制御は HTTP 中継パス固有の機能)。
- Admin MCP (`/admin/mcp`) の Streamable HTTP は既存の `tests/unit/mcp/test_admin_mcp.py` で
  カバー済み。本ファイルはメインの MCP エンドポイント(`/mcp`, `/<id>/mcp`)を対象とする。
- 深度ヘッダー(`X-AccelMCP-Depth`)の伝播は **MCP中継パス**固有の機能であり、API中継
  (`_execute_api_call`、連鎖の終端)では付与されない。連結のループ防止は AccelMCP 同士の
  MCP中継連鎖を対象とする設計のため。
- 結合テストは werkzeug の実サーバーをスレッド起動するため、ユニットより低速
  (約6秒)。`@pytest.mark.integration` を付与しているので `-m "not integration"` で除外可能。
