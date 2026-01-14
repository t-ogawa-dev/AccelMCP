"""
MCP Server Application Factory
"""
import os
import logging
from flask import Flask
from flask_cors import CORS

# Application version
__version__ = "1.0.0"

# Import extensions
from app.models.models import db
from app.config.config import Config
from flask_migrate import Migrate


def setup_logging(app):
    """Configure application logging"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Set log level
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set Flask app logger
    app.logger.setLevel(numeric_level)
    
    # Set werkzeug logger (Flask dev server)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(numeric_level)
    
    app.logger.info(f"Logging configured with level: {log_level}")


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__,
                template_folder='views/templates',
                static_folder='assets')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Store admin credentials in app config (only if not already set by config class)
    if 'ADMIN_USERNAME' not in app.config or app.config.get('TESTING'):
        # In testing mode, don't override with env vars
        if not app.config.get('TESTING'):
            app.config['ADMIN_USERNAME'] = os.getenv('ADMIN_USERNAME', 'admin')
            app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    app.logger.debug(f"Admin username: {app.config['ADMIN_USERNAME']}")
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db, directory='db/migrations')
    CORS(app)
    
    app.logger.info("Database and extensions initialized")
    
    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.api_controller import api_bp
    from app.controllers.mcp_controller import mcp_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(mcp_bp)
    
    app.logger.info("All blueprints registered")
    
    return app
