"""
Run script for MCP Server
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get environment and log level
    flask_env = os.getenv('FLASK_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    is_debug = flask_env == 'development'
    
    app.logger.info(f"Starting Flask application on port 5000")
    app.logger.info(f"Environment: {flask_env}")
    app.logger.info(f"Log level: {log_level}")
    app.logger.info(f"Debug mode: {is_debug}")
    
    app.run(host='0.0.0.0', port=5000, debug=is_debug)
