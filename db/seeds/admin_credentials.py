"""
Seed admin credentials and system connection account.

This script is called automatically at app startup if no AdminCredentials
record exists. It reads the initial username/password from the environment
(ADMIN_USERNAME / ADMIN_PASSWORD) and the initial API key from
ACCELMCP_ADMIN_API_KEY, then creates:

  1. One AdminCredentials record with is_initialized=False
     (forces credential change on first login)
  2. One system ConnectionAccount for Admin MCP Bearer authentication
"""

import os
import secrets


def seed_admin_credentials(app):
    """Create initial admin credentials and system account if they don't exist."""
    from app.models.models import AdminCredentials, ConnectionAccount, db

    with app.app_context():
        # --- AdminCredentials ---
        if AdminCredentials.query.count() == 0:
            username = os.getenv("ADMIN_USERNAME", "accel")
            password = os.getenv("ADMIN_PASSWORD", "universe")

            cred = AdminCredentials(is_initialized=False)
            cred.username = username
            cred.set_password(password)
            db.session.add(cred)
            app.logger.info(
                f"[seed] Created AdminCredentials for username='{username}' (is_initialized=False)"
            )

        # --- System ConnectionAccount (Admin MCP API key) ---
        system_account = ConnectionAccount.query.filter_by(is_system=True).first()
        if system_account is None:
            initial_token = os.getenv(
                "ACCELMCP_ADMIN_API_KEY", secrets.token_urlsafe(32)
            )
            system_account = ConnectionAccount(
                name="AccelMCP Admin",
                bearer_token=initial_token,
                notes="System account for Admin MCP endpoint. Do not delete.",
                is_system=True,
            )
            db.session.add(system_account)
            app.logger.info("[seed] Created system ConnectionAccount for Admin MCP")

        db.session.commit()


if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from app import create_app

    seed_admin_credentials(create_app())
    print("Admin credentials seeded.")
