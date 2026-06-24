---
title: Home
---

# AccelMCP

HTTP/stdio compatible MCP server with API/MCP relay functionality and user-based permission
management via a Web admin interface.

[GitHub Repository](https://github.com/t-ogawa-dev/AccelMCP){ .md-button .md-button--primary }
[日本語ドキュメント](../index.md){ .md-button }

![AccelMCP architecture overview](../assets/diagrams/architecture-overview.svg)

## Key Features

- **MCP Protocol Support**: Compatible with both HTTP and stdio, including Streamable HTTP (SSE)
- **Relay Functionality**: Relay to API and MCP servers, including daisy-chaining multiple AccelMCP instances
- **Permission Management**: User-specific Tool usage permission control (3-tier hierarchy)
- **Web Admin Interface**: Manage Services, Capabilities, Accounts, and admin users
- **Bearer Token Authentication**: Per-account token generation
- **Horizontal Scaling**: Split WEB / MCP containers and share sessions via Redis to scale out

## Screenshots

!!! note
    The screenshots below show the default Japanese UI. AccelMCP also ships with a
    built-in English UI, switchable from the language dropdown in the top-right corner.

![Login screen](../assets/screenshots/login.png)
*Login screen*

![Dashboard](../assets/screenshots/dashboard.png)
*Dashboard — entry point to every admin feature*

![MCP services list](../assets/screenshots/mcp-services-list.png)
*MCP services list — shows public/restricted access control at a glance*

![MCP service detail](../assets/screenshots/mcp-service-detail.png)
*MCP service detail — auto-generated client configuration snippets for Claude Desktop / Cursor / VS Code*

![AdminMCP connection guide](../assets/screenshots/guide.png)
*AdminMCP connection guide — endpoint info and the list of available tools*

![Connection logs](../assets/screenshots/connection-logs.png)
*Connection logs — review connection history per MCP service*

![Connection accounts list](../assets/screenshots/accounts-list.png)
*Connection accounts list — issue Bearer tokens for MCP clients*

## Documentation

| Document | Description |
| --- | --- |
| [Quick Start](QUICKSTART.en.md) | Fastest way to start and test the MCP server in 5 minutes |
| [Setup Guide](SETUP.en.md) | Detailed setup and startup instructions |
| [MCP Endpoints](MCP_ENDPOINTS.en.md) | Detailed usage of each MCP server endpoint |
| [Directory Structure](STRUCTURE.en.md) | Project structure based on MVC pattern |
| [Testing Guide](TESTING.en.md) | How to run unit and integration tests |
| [E2E Testing](E2E_TESTING.en.md) | How to run E2E tests with Playwright |
| [Database Migration](MIGRATION.en.md) | Database migration management with Flask-Migrate (Alembic) |
| [Scaling & Containers](SCALING.en.md) | Container layout, single-host vs. multi-host, Redis-backed sessions |

## About This Project

This project was built **100% through vibe coding** — all code was implemented via pair
programming with AI.

**Models used:** Claude Sonnet 4.5 / 4.6, Claude Opus 4.8
