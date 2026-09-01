"""
Configuration settings for MCP Server
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///mcp.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Admin authentication
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

    # Admin MCP API key (Bearer token for /admin/mcp endpoint)
    ADMIN_API_KEY = os.getenv("ACCELMCP_ADMIN_API_KEY", "")

    # Flask settings
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    TESTING = False

    # Streamable HTTP session store backend.
    # When set, MCP/Admin-MCP Streamable HTTP sessions are shared via Redis so the MCP
    # endpoint can be scaled across replicas/hosts. When unset, an in-process store is
    # used (fine for a single container). Example: redis://redis:6379/0
    REDIS_URL = os.getenv("REDIS_URL")

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv("SESSION_LIFETIME_HOURS", "12")))
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Allow cookies to work across localhost and lvh.me (development only)
    SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN", None)

    # Template Repository Configuration
    TEMPLATE_REPOSITORY_URL = os.getenv(
        "TEMPLATE_REPOSITORY_URL", "https://raw.githubusercontent.com/t-ogawa-dev/octopus-mcp-proxy/main/data/builtin_templates"
    )
    TEMPLATE_INDEX_FILE = os.getenv("TEMPLATE_INDEX_FILE", "index.yaml")
    TEMPLATE_VERSIONS_DIR = os.getenv("TEMPLATE_VERSIONS_DIR", "versions")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
