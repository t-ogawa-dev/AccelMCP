"""
Tests for:
- /guide page route
- GET /api/admin/system-account
- POST /api/admin/system-account/regenerate
"""

import json

import pytest

from app.models.models import ConnectionAccount


@pytest.fixture
def system_account(db):
    """Create system account for testing."""
    acc = ConnectionAccount(
        name="AccelMCP Admin System",
        bearer_token="initial-test-token-abc123",
        is_system=True,
    )
    db.session.add(acc)
    db.session.commit()
    return acc


@pytest.fixture
def regular_account(db):
    """Create a non-system account for testing."""
    acc = ConnectionAccount(
        name="Regular User",
        bearer_token="regular-user-token-xyz",
        is_system=False,
    )
    db.session.add(acc)
    db.session.commit()
    return acc


# ---------------------------------------------------------------------------
# /guide page
# ---------------------------------------------------------------------------


class TestGuideRoute:
    def test_guide_requires_login(self, client, db):
        """Unauthenticated access should redirect."""
        resp = client.get("/guide")
        assert resp.status_code in (302, 401)

    def test_guide_returns_200_when_logged_in(self, auth_client, db):
        """Authenticated access should return 200."""
        resp = auth_client.get("/guide")
        assert resp.status_code == 200

    def test_guide_contains_admin_tools(self, auth_client, db):
        """Guide page HTML should include admin tool names."""
        resp = auth_client.get("/guide")
        body = resp.data.decode()
        assert "get_dashboard_summary" in body
        assert "list_mcp_services" in body
        assert "create_mcp_service" in body

    def test_guide_includes_all_twelve_tools(self, auth_client, db):
        """Guide page should list all 12 admin tools."""
        from app.controllers.admin_mcp_controller import ADMIN_TOOLS

        resp = auth_client.get("/guide")
        body = resp.data.decode()
        for tool in ADMIN_TOOLS:
            assert tool["name"] in body, f"Tool '{tool['name']}' not found in guide page"


# ---------------------------------------------------------------------------
# GET /api/admin/system-account
# ---------------------------------------------------------------------------


class TestGetSystemAccount:
    def test_requires_login(self, client, db, system_account):
        """Unauthenticated request should fail."""
        resp = client.get("/api/admin/system-account")
        assert resp.status_code in (302, 401)

    def test_returns_404_when_no_system_account(self, auth_client, db):
        """Should return 404 when no system account exists."""
        resp = auth_client.get("/api/admin/system-account")
        assert resp.status_code == 404
        data = json.loads(resp.data)
        assert "error" in data

    def test_returns_system_account(self, auth_client, db, system_account):
        """Should return id and bearer_token."""
        resp = auth_client.get("/api/admin/system-account")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["id"] == system_account.id
        assert data["bearer_token"] == "initial-test-token-abc123"

    def test_does_not_return_regular_account(self, auth_client, db, regular_account):
        """Without system account, should still return 404."""
        resp = auth_client.get("/api/admin/system-account")
        assert resp.status_code == 404

    def test_returns_only_system_account_when_both_exist(self, auth_client, db, system_account, regular_account):
        """Should return only the system account, not regular accounts."""
        resp = auth_client.get("/api/admin/system-account")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["bearer_token"] == system_account.bearer_token


# ---------------------------------------------------------------------------
# POST /api/admin/system-account/regenerate
# ---------------------------------------------------------------------------


class TestRegenerateSystemAccount:
    def test_requires_login(self, client, db, system_account):
        """Unauthenticated request should fail."""
        resp = client.post("/api/admin/system-account/regenerate")
        assert resp.status_code in (302, 401)

    def test_returns_404_when_no_system_account(self, auth_client, db):
        """Should return 404 when no system account exists."""
        resp = auth_client.post("/api/admin/system-account/regenerate")
        assert resp.status_code == 404

    def test_regenerates_token(self, auth_client, db, system_account):
        """Should return new bearer_token different from original."""
        original_token = system_account.bearer_token
        resp = auth_client.post("/api/admin/system-account/regenerate")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["success"] is True
        assert "bearer_token" in data
        assert data["bearer_token"] != original_token

    def test_regenerated_token_is_persisted(self, auth_client, db, system_account):
        """Regenerated token should be saved in the database."""
        resp = auth_client.post("/api/admin/system-account/regenerate")
        new_token = json.loads(resp.data)["bearer_token"]

        db.session.refresh(system_account)
        assert system_account.bearer_token == new_token

    def test_repeated_regeneration_produces_different_tokens(self, auth_client, db, system_account):
        """Two consecutive regenerations should produce different tokens."""
        resp1 = auth_client.post("/api/admin/system-account/regenerate")
        token1 = json.loads(resp1.data)["bearer_token"]

        resp2 = auth_client.post("/api/admin/system-account/regenerate")
        token2 = json.loads(resp2.data)["bearer_token"]

        assert token1 != token2

    def test_regenerated_token_length_is_adequate(self, auth_client, db, system_account):
        """secrets.token_urlsafe(32) produces ~43 chars; must be > 30."""
        resp = auth_client.post("/api/admin/system-account/regenerate")
        token = json.loads(resp.data)["bearer_token"]
        assert len(token) > 30
