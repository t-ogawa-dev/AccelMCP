[日本語](../SCALING.md) | English

# Scaling & Container Layout

AccelMCP runs both single-host and multi-host deployments **from the same image**.
By splitting the roles (WEB admin UI / MCP endpoint) into separate containers and sharing
Streamable HTTP sessions through Redis, the MCP endpoint can be scaled horizontally on its own.

## Container Layout

| Service | Role | Notes |
| --- | --- | --- |
| `caddy` | Reverse proxy / TLS | Routes by path to `web` and `mcp` |
| `web` | Admin UI + REST API | Runs DB migrations on startup |
| `mcp` | MCP endpoint | Same image as `web`; does NOT run migrations |
| `redis` | Shared session store | Holds Streamable HTTP sessions |
| `db` | PostgreSQL | Application data |

`web` and `mcp` use the **same image and the same app** (all blueprints registered); Caddy routes
requests by path. This is what lets "all-in-one on one host" and "role-split across hosts" both run
from the same compose definition.

### Caddy routing

| Path | Routed to |
| --- | --- |
| `/mcp`, `/mcp/<subdomain>`, `/<identifier>/mcp`, `/admin/mcp`, `/tools/*` | `mcp` |
| Everything else (`/`, `/dashboard`, `/api/*`, `/assets/*`, etc.) | `web` |

## 1. Single-host (all-in-one)

Like Dify, run all containers on one host.

```bash
docker compose up -d
```

- `web` / `mcp` / `redis` / `db` / `caddy` all run on the same host.
- Because Redis is present, Streamable HTTP sessions are stored in Redis, but a single host can
  also run with in-memory sessions (see below).

## 2. About the session store (Redis)

Streamable HTTP validates the `Mcp-Session-Id` issued at `initialize` on subsequent requests.
When the MCP endpoint runs as **multiple replicas / multiple hosts**, a follow-up request routed to
a different replica can no longer recognize the session, so the session must live in a shared store.

- When `REDIS_URL` is **set**: sessions are stored in Redis (shared).
  - Example: `REDIS_URL=redis://redis:6379/0`
  - Even with multiple `mcp` replicas, any replica can validate the session.
- When `REDIS_URL` is **unset**: sessions are stored in process memory.
  - No extra infrastructure required. This is sufficient for **single-host, single-process** runs.
  - Not usable with multiple replicas, since sessions are not shared between them.

`compose.yaml` passes `REDIS_URL=redis://redis:6379/0` by default. To run a single-instance setup
without Redis, leave `REDIS_URL` empty.

## 3. Scaling only the MCP endpoint

To add replicas on the same host:

```bash
docker compose up -d --scale mcp=3
```

(Caddy's `reverse_proxy mcp:5000` load-balances across replicas via Docker DNS round-robin. Because
sessions are shared through `REDIS_URL`, any replica that receives a follow-up request stays consistent.)

## 4. Spreading across multiple hosts

To run WEB / MCP / Redis / DB on separate hosts, start only the services each host needs and point
their endpoints at each host's address via environment variables and the Caddy config.

- `web` host: `web` + `caddy` (or a separate LB)
- `mcp` host(s): `mcp` (point `REDIS_URL` / `DATABASE_URL` at the shared Redis / shared DB)
- `redis` host: `redis`
- `db` host: PostgreSQL

Key points:

- `mcp` does NOT run migrations (`web` does). Schema updates happen once, during the `web` deployment.
- All `mcp` replicas must reference the **same `REDIS_URL` and the same `DATABASE_URL`**.
- Caddy (or an upstream LB) must route MCP paths to the `mcp` group and everything else to `web`.

## Related implementation

- Session store abstraction: [app/services/session_store.py](../../app/services/session_store.py)
  - `InMemorySessionStore` / `RedisSessionStore` / `get_session_store(namespace)`
  - Sessions are isolated by namespace: `"mcp"` (the MCP endpoint) and `"admin"` (Admin MCP)
- Session usage:
  - [app/controllers/mcp_controller.py](../../app/controllers/mcp_controller.py)
  - [app/controllers/admin_mcp_controller.py](../../app/controllers/admin_mcp_controller.py)

## Tests

- `tests/unit/infrastructure/test_session_store.py` — unit tests for the session store
  (in-memory / Redis / backend selection)
- `tests/unit/mcp/test_relay_and_streamable.py::TestStreamableHttpRedisSession` —
  Streamable HTTP session round-trip on the Redis backend
- `tests/integration/test_streamable_chain.py` — multi-hop Streamable HTTP chaining with real servers
