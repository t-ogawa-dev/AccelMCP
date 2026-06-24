"""
Run script for MCP Server
"""
import os
from app import create_app

app = create_app()

# Seed admin credentials after migration (only when running the server, not tests)
if not app.config.get("TESTING"):
    try:
        from db.seeds.admin_credentials import seed_admin_credentials
        seed_admin_credentials(app)
    except Exception as e:
        app.logger.warning(f"Admin credentials seed skipped: {e}")

if __name__ == '__main__':
    # Get environment and log level
    flask_env = os.getenv('FLASK_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    is_debug = flask_env == 'development'
    
    # Port can be configured via environment variable (default: 5000)
    port = int(os.getenv('FLASK_PORT', os.getenv('PORT', 5000)))
    
    app.logger.info(f"Starting Flask application on port {port}")
    app.logger.info(f"Environment: {flask_env}")
    app.logger.info(f"Log level: {log_level}")
    app.logger.info(f"Debug mode: {is_debug}")
    
    app.run(host='0.0.0.0', port=port, debug=is_debug)
