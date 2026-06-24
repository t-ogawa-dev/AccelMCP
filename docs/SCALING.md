[English](en/SCALING.en.md) | 日本語

# スケーリングとコンテナ構成

AccelMCP は **同一イメージのまま**、1台運用にも複数台運用にも対応します。
役割(WEB管理画面 / MCPエンドポイント)を別コンテナに分け、Streamable HTTP の
セッションを Redis で共有することで、MCP エンドポイントだけを水平スケールできます。

## コンテナ構成

| サービス | 役割 | 備考 |
| --- | --- | --- |
| `caddy` | リバースプロキシ / TLS | パスで `web` と `mcp` に振り分け |
| `web` | 管理UI + REST API | 起動時に DB マイグレーションを実行 |
| `mcp` | MCP エンドポイント | `web` と同一イメージ。マイグレーションは実行しない |
| `redis` | セッション共有ストア | Streamable HTTP セッションを保持 |
| `db` | PostgreSQL | アプリのデータ |

`web` と `mcp` は **同じイメージ・同じアプリ**(全Blueprint登録)で、Caddy が
リクエストのパスで振り分けます。これにより「全部入り1台」も「役割分担の複数台」も
同じ compose 定義で動きます。

### Caddy のルーティング

| パス | 振り分け先 |
| --- | --- |
| `/mcp`, `/mcp/<subdomain>`, `/<identifier>/mcp`, `/admin/mcp`, `/tools/*` | `mcp` |
| 上記以外(`/`, `/dashboard`, `/api/*`, `/assets/*` など) | `web` |

## 1. 1台運用(全部入り)

Dify と同様に、1つのホストで全コンテナを起動します。

```bash
docker compose up -d
```

- `web` / `mcp` / `redis` / `db` / `caddy` が同一ホストで動きます。
- Redis があるので Streamable HTTP セッションは Redis に保存されますが、
  1台なら in-memory でも動作します(後述)。

## 2. セッションストア(Redis)について

Streamable HTTP は `initialize` で発行した `Mcp-Session-Id` を後続リクエストで
検証します。MCP エンドポイントを**複数レプリカ/複数ホスト**にすると、後続リクエストが
別レプリカに振られた際にセッションを認識できなくなるため、セッションを共有ストアに
置く必要があります。

- 環境変数 `REDIS_URL` が **設定されている**場合: Redis にセッションを保存(共有)。
  - 例: `REDIS_URL=redis://redis:6379/0`
  - `mcp` を複数レプリカ化しても、どのレプリカでもセッションを検証できます。
- 環境変数 `REDIS_URL` が **未設定**の場合: プロセス内メモリに保存。
  - 追加インフラ不要。**1台・単一プロセス運用**ならこれで十分です。
  - 複数レプリカにするとセッションがレプリカ間で共有されないので不可。

`compose.yaml` ではデフォルトで `REDIS_URL=redis://redis:6379/0` を渡しています。
Redis を使いたくない単一構成にする場合は `REDIS_URL` を空にしてください。

## 3. MCP エンドポイントだけスケールする

同一ホストでレプリカを増やす場合:

```bash
docker compose up -d --scale mcp=3
```

(Caddy の `reverse_proxy mcp:5000` は Docker DNS のラウンドロビンで複数レプリカに
分散します。`REDIS_URL` でセッションが共有されているため、どのレプリカが後続
リクエストを受けても整合します。)

## 4. 複数ホストに分散する

WEB / MCP / Redis / DB を別々のホストで動かす場合は、各ホストで必要なサービスだけを
起動し、接続先を環境変数・Caddy 設定で各ホストのアドレスに変更します。

- `web` ホスト: `web` + `caddy`(または別途LB)
- `mcp` ホスト(複数可): `mcp`(`REDIS_URL`/`DATABASE_URL` を共有Redis/共有DBに向ける)
- `redis` ホスト: `redis`
- `db` ホスト: PostgreSQL

ポイント:

- `mcp` はマイグレーションを実行しません(`web` が実行)。スキーマ更新は `web` 側の
  デプロイで一度だけ行われます。
- すべての `mcp` レプリカが**同じ `REDIS_URL` と同じ `DATABASE_URL`** を参照すること。
- Caddy(または前段のLB)で MCP パスを `mcp` 群へ、それ以外を `web` へ振り分けること。

## 関連する実装

- セッションストア抽象化: [app/services/session_store.py](https://github.com/t-ogawa-dev/AccelMCP/blob/main/app/services/session_store.py)
  - `InMemorySessionStore` / `RedisSessionStore` / `get_session_store(namespace)`
  - 名前空間 `"mcp"`(MCP本体)と `"admin"`(Admin MCP)でセッションを分離
- セッション利用箇所:
  - [app/controllers/mcp_controller.py](https://github.com/t-ogawa-dev/AccelMCP/blob/main/app/controllers/mcp_controller.py)
  - [app/controllers/admin_mcp_controller.py](https://github.com/t-ogawa-dev/AccelMCP/blob/main/app/controllers/admin_mcp_controller.py)

## テスト

- `tests/unit/infrastructure/test_session_store.py` — セッションストア(in-memory / Redis /
  バックエンド選択)のユニットテスト
- `tests/unit/mcp/test_relay_and_streamable.py::TestStreamableHttpRedisSession` —
  Redis バックエンドでの Streamable HTTP セッション往復
- `tests/integration/test_streamable_chain.py` — 実サーバー多段の Streamable HTTP 連結
