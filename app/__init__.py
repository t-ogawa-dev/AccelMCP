"""
MCP Server Application Factory
"""
import os
from flask import Flask
from flask_cors import CORS

# Import extensions
from app.models.models import db
from app.config.config import Config
from flask_migrate import Migrate


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__,
                template_folder='views/templates',
                static_folder='assets')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Store admin credentials in app config
    app.config['ADMIN_USERNAME'] = os.getenv('ADMIN_USERNAME', 'admin')
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db, directory='db/migrations')
    CORS(app)
    
    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.api_controller import api_bp
    from app.controllers.mcp_controller import mcp_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(mcp_bp)
    
    return app
