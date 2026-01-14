"""
Configuration settings for MCP Server
"""
import os
from datetime import timedelta


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mcp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admin authentication (Built by Accel Universe branding)
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'accel')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'universe')
    
    # Flask settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv('SESSION_LIFETIME_HOURS', '12')))
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Template Repository Configuration
    TEMPLATE_REPOSITORY_URL = os.getenv('TEMPLATE_REPOSITORY_URL', 
                                         'https://raw.githubusercontent.com/t-ogawa-dev/AccelMCP/main/data/builtin_templates')
    TEMPLATE_INDEX_FILE = os.getenv('TEMPLATE_INDEX_FILE', 'index.yaml')
    TEMPLATE_VERSIONS_DIR = os.getenv('TEMPLATE_VERSIONS_DIR', 'versions')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
