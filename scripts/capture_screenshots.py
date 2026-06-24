"""
Capture screenshots of the AccelMCP admin UI for the documentation site.

Spins up a real AccelMCP instance against a temporary SQLite DB, seeds a small
amount of sample data so the screens don't look empty, then drives a headless
Chromium browser (Playwright) to capture PNG screenshots into
docs/assets/screenshots/.

Usage:
    source .venv/bin/activate
    python scripts/capture_screenshots.py

Requires the `playwright` package and the Chromium browser to be installed:
    pip install playwright
    playwright install chromium
"""

import contextlib
import json
import os
import secrets
import sys
import tempfile
import threading
import time
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "docs" / "assets" / "screenshots"
VIEWPORT = {"width": 1440, "height": 900}


class _QuietHandler(WSGIRequestHandler):
    def log_message(self, *args, **kwargs):
        pass


class _ServerThread:
    def __init__(self, wsgi_app):
        self.server = make_server("127.0.0.1", 0, wsgi_app, handler_class=_QuietHandler)
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        return self

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.port}"

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


def _wait_until_up(url, timeout=5.0):
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            httpx.get(url, timeout=1.0)
            return
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.05)
    raise RuntimeError(f"Server did not come up: {last_err}")


def _make_app(db_path):
    from app import create_app
    from app.config.config import Config

    class _Cfg(Config):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        WTF_CSRF_ENABLED = False
        SECRET_KEY = "screenshot-secret"

    return create_app(_Cfg)


def _seed_sample_data(app):
    """Create enough sample data for the screens to look representative."""
    from app.models.models import (
        AdminCredentials,
        Capability,
        ConnectionAccount,
        McpConnectionLog,
        McpService,
        Service,
        db,
    )
    from db.seeds.admin_credentials import seed_admin_credentials

    with app.app_context():
        db.create_all()
        seed_admin_credentials(app)

        weather = McpService(
            name="Weather Hub",
            identifier="weather-hub",
            routing_type="path",
            description="Public weather lookup tools for agents.",
            access_control="public",
            is_enabled=True,
        )
        internal = McpService(
            name="Internal Docs",
            identifier="internal-docs",
            routing_type="subdomain",
            description="Restricted internal knowledge base access.",
            access_control="restricted",
            is_enabled=True,
        )
        db.session.add_all([weather, internal])
        db.session.commit()

        weather_app = Service(
            name="OpenWeather API",
            service_type="api",
            mcp_url="https://api.openweathermap.org/data/2.5",
            common_headers="{}",
            description="Relays to the OpenWeather REST API.",
            mcp_service_id=weather.id,
            is_enabled=True,
            access_control="public",
        )
        db.session.add(weather_app)
        db.session.commit()

        cap1 = Capability(
            name="get_current_weather",
            description="Get the current weather for a given city.",
            capability_type="tool",
            app_id=weather_app.id,
            url="https://api.openweathermap.org/data/2.5/weather",
            headers="{}",
            body_params=json.dumps(
                {"properties": {"city": {"type": "string", "description": "City name"}}, "required": ["city"]}
            ),
            is_enabled=True,
            access_control="public",
        )
        cap2 = Capability(
            name="get_forecast",
            description="Get the 5-day weather forecast for a given city.",
            capability_type="tool",
            app_id=weather_app.id,
            url="https://api.openweathermap.org/data/2.5/forecast",
            headers="{}",
            body_params=json.dumps(
                {"properties": {"city": {"type": "string", "description": "City name"}}, "required": ["city"]}
            ),
            is_enabled=True,
            access_control="public",
        )
        db.session.add_all([cap1, cap2])
        db.session.commit()

        account = ConnectionAccount(
            name="Claude Desktop",
            bearer_token=secrets.token_urlsafe(32),
            notes="Production client used by the team.",
        )
        db.session.add(account)
        db.session.commit()

        log1 = McpConnectionLog(
            mcp_method="tools/call",
            tool_name="get_current_weather",
            mcp_service_id=weather.id,
            mcp_service_name=weather.name,
            app_id=weather_app.id,
            app_name=weather_app.name,
            capability_id=cap1.id,
            capability_name=cap1.name,
            status_code=200,
            is_success=True,
            duration_ms=184,
            ip_address="203.0.113.10",
            access_control="public",
        )
        log2 = McpConnectionLog(
            mcp_method="tools/call",
            tool_name="get_forecast",
            mcp_service_id=weather.id,
            mcp_service_name=weather.name,
            app_id=weather_app.id,
            app_name=weather_app.name,
            capability_id=cap2.id,
            capability_name=cap2.name,
            status_code=504,
            is_success=False,
            error_message="Upstream timeout",
            duration_ms=30021,
            ip_address="203.0.113.10",
            access_control="public",
        )
        db.session.add_all([log1, log2])
        db.session.commit()

        cred = AdminCredentials.query.first()
        return cred.username, weather.id, account.id


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["TESTING"] = ""  # ensure non-testing seed code path is not skipped oddly

    fd, db_path = tempfile.mkstemp(suffix="_screenshots.db")
    os.close(fd)
    server = None
    try:
        app = _make_app(db_path)
        username, mcp_service_id, account_id = _seed_sample_data(app)

        server = _ServerThread(app).start()
        _wait_until_up(f"{server.base_url}/health")
        base = server.base_url

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(viewport=VIEWPORT, locale="ja-JP")
            page = context.new_page()

            # 1. Login page
            page.goto(f"{base}/login")
            page.wait_for_selector('input[name="username"]')
            page.screenshot(path=str(OUTPUT_DIR / "login.png"))

            # 2. Log in (triggers forced credential-change redirect on first login)
            page.fill('input[name="username"]', username)
            page.fill('input[name="password"]', "universe")
            with page.expect_navigation():
                page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")

            if "/change-credentials" in page.url:
                page.wait_for_selector("#change-credentials-form")
                page.screenshot(path=str(OUTPUT_DIR / "change-credentials.png"))
                # Complete the forced change out-of-band so the rest of the
                # walkthrough isn't blocked by the redirect.
                with app.app_context():
                    from app.models.models import AdminCredentials, db

                    cred = AdminCredentials.query.first()
                    cred.is_initialized = True
                    db.session.commit()

            # 3. Dashboard
            page.goto(f"{base}/dashboard")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(OUTPUT_DIR / "dashboard.png"))

            # 4. MCP services list
            page.goto(f"{base}/mcp-services")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUTPUT_DIR / "mcp-services-list.png"))

            # 5. MCP service detail
            page.goto(f"{base}/mcp-services/{mcp_service_id}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUTPUT_DIR / "mcp-service-detail.png"))

            # 6. Connection accounts list
            page.goto(f"{base}/accounts")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUTPUT_DIR / "accounts-list.png"))

            # 7. Connection guide (Admin MCP endpoint info)
            page.goto(f"{base}/guide")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUTPUT_DIR / "guide.png"))

            # 8. Connection logs
            page.goto(f"{base}/connection-logs")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUTPUT_DIR / "connection-logs.png"))

            browser.close()

        print(f"Screenshots written to {OUTPUT_DIR}")
    finally:
        if server is not None:
            server.stop()
        with contextlib.suppress(OSError):
            os.unlink(db_path)


if __name__ == "__main__":
    main()
