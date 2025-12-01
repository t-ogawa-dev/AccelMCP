"""
Run script for MCP Server
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    app.logger.info(f"Starting Flask application on port 5000 with log level {log_level}")
    app.run(host='0.0.0.0', port=5000, debug=True)
