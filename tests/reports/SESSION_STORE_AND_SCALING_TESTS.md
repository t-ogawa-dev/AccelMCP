# Session Store & Scaling Tests

テスト対象: Streamable HTTP セッションの共有ストア化(Redis)と、WEB/MCP のコンテナ分離・
水平スケール対応

作成日: 2026-06-24

## 背景・目的

AccelMCP を「1台運用(全部入り compose up)」と「複数台運用(WEB/MCP/Redis を別サーバに
分散)」の両方で動かせるようにする。特に MCP エンドポイントを複数レプリカ/複数ホストに
スケールするには、Streamable HTTP の `Mcp-Session-Id` をプロセス内メモリではなく**共有
ストア(Redis)**に置く必要がある(後続リクエストが別レプリカに振られてもセッションを
認識できるように)。

## 実装変更

| 変更 | 内容 |
| --- | --- |
| `app/services/session_store.py` (新規) | セッションストア抽象化。`InMemorySessionStore` / `RedisSessionStore` / `get_session_store(namespace)`。`REDIS_URL` があれば Redis、なければ in-memory に自動フォールバック。名前空間で `mcp` と `admin` を分離 |
| `app/controllers/mcp_controller.py` | モジュール内 dict (`_active_sessions`) を廃止し `get_session_store("mcp")` に置換。`_remove_session` を追加 |
| `app/controllers/admin_mcp_controller.py` | 同上(`_admin_sessions` を廃止、`get_session_store("admin")` に置換) |
| `app/config/config.py` | `REDIS_URL` 設定を追加 |
| `requirements.txt` | `redis==5.0.1`(本体)、`fakeredis==2.21.1`(テスト)を追加 |
| `compose.yaml` | `redis` サービスと `mcp` サービス(web と同一イメージ)を追加。`REDIS_URL` を web/mcp に注入。マイグレーションは web のみ実行 |
| `Caddyfile` / `Caddyfile.prod` | MCP パス(`/mcp`, `/<id>/mcp`, `/admin/mcp`, `/tools/*`)を `mcp` へ、それ以外を `web` へ振り分け |
| `docs/SCALING.md` (新規) | コンテナ構成・1台/複数台運用・スケール手順のドキュメント |

設計判断: web と mcp は**同一イメージ・全機能**のまま、Caddy がパスで振り分ける方式を採用。
これにより create_app の分岐なしで、1台運用と複数台運用を同じ compose・同じイメージで両立できる
(Dify の api/worker が同一イメージで command だけ違うのと同じ考え方)。

## 新規テストファイル (1)

`tests/unit/infrastructure/test_session_store.py` (20 tests, 全件成功)

### `TestInMemorySessionStore` (6 tests)

- register/validate、未登録は無効、remove、未登録removeはno-op
- TTL 失効後は無効、register 時に失効セッションが掃除される

### `TestRedisSessionStore` (6 tests) — fakeredis 使用

- register/validate、未登録は無効、remove
- `test_key_is_namespaced` — Redis キーに名前空間プレフィックスが付く
- `test_ttl_is_applied` — `SETEX` の TTL が効いている
- `test_two_namespaces_do_not_collide` — mcp/admin で同一IDが衝突しない

### `TestGetSessionStore` (5 tests) — バックエンド選択

- `REDIS_URL` 未設定 → InMemory、設定 → Redis
- 同一名前空間はキャッシュされ同一インスタンス、別名前空間は別インスタンス
- `reset_session_stores()` でバックエンド再選択

### `TestControllerHelpersUseStore` (3 tests) — コントローラ統合

- mcp / admin それぞれの `_register_session` → `_is_valid_session` → `_remove_session` 往復
- mcp と admin のセッションが名前空間で分離されている

## 新規テスト (2) — 既存ファイルへ追加

`tests/unit/mcp/test_relay_and_streamable.py::TestStreamableHttpRedisSession` (1 test)

- `test_session_roundtrip_with_redis_backend` — `REDIS_URL` を設定し fakeredis を共有
  バックエンドにして、実際の `/mcp` エンドポイント経由で:
  1. initialize でセッションが Redis に作成される(キー `accelmcp:session:mcp:<id>` を確認)
  2. 別リクエストが Redis 経由でセッション検証して成功
  3. DELETE で Redis からセッションが削除される
  を検証。**MCP エンドポイントを複数レプリカ化してもセッションが共有される**ことの根拠。

## テスト実行

```bash
python -m pytest tests/unit/infrastructure/test_session_store.py -v
python -m pytest tests/unit/mcp/test_relay_and_streamable.py::TestStreamableHttpRedisSession -v
```

## テスト結果

```
tests/unit/infrastructure/test_session_store.py:                      20 passed
tests/unit/mcp/test_relay_and_streamable.py (Redis session 追加分含む): 18 passed
tests/unit/ + tests/integration/ (全体):                             368 passed  ※回帰なし
```

## 設定/構成の検証

- `docker compose config` — compose.yaml 構文検証 OK
- `caddy validate` — Caddyfile / Caddyfile.prod ともに Valid configuration

## 補足

- `REDIS_URL` 未設定時は in-memory にフォールバックするため、**1台・単一プロセス運用では
  Redis は必須ではない**。複数レプリカ/複数ホストにする場合のみ Redis が必要。
- web と mcp は同一イメージのため Docker ビルドは1回。実行時に Caddy がパスで振り分ける。
- 詳細な運用手順は [docs/SCALING.md](../../docs/SCALING.md) を参照。
