"""
Database Migration Management Script

Usage:
    python migrate.py init              # Initialize migrations directory
    python migrate.py migrate           # Generate new migration
    python migrate.py upgrade           # Apply migrations
    python migrate.py downgrade         # Revert last migration
    python migrate.py current           # Show current revision
    python migrate.py history           # Show migration history
    python migrate.py stamp             # Stamp the database with a specific revision
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask_migrate import init, migrate, upgrade, downgrade, current, history, stamp
from app import create_app

app = create_app()
MIGRATION_DIR = 'db/migrations'

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    with app.app_context():
        if command == 'init':
            print(f"Initializing migrations directory at {MIGRATION_DIR}...")
            init(directory=MIGRATION_DIR)
        elif command == 'migrate':
            message = sys.argv[2] if len(sys.argv) > 2 else 'Auto migration'
            print(f"Creating migration: {message}")
            migrate(message=message, directory=MIGRATION_DIR)
        elif command == 'upgrade':
            revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
            print(f"Upgrading to {revision}...")
            upgrade(revision=revision, directory=MIGRATION_DIR)
        elif command == 'downgrade':
            revision = sys.argv[2] if len(sys.argv) > 2 else '-1'
            print(f"Downgrading to {revision}...")
            downgrade(revision=revision, directory=MIGRATION_DIR)
        elif command == 'current':
            print("Current database revision:")
            current(directory=MIGRATION_DIR)
        elif command == 'history':
            print("Migration history:")
            history(directory=MIGRATION_DIR)
        elif command == 'stamp':
            revision = sys.argv[2] if len(sys.argv) > 2 else 'head'
            print(f"Stamping database with revision {revision}...")
            stamp(revision=revision, directory=MIGRATION_DIR)
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)

if __name__ == '__main__':
    main()
