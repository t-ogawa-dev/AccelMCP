"""
Seed security-related admin settings
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.models import db, AdminSettings


def seed_security_settings(app):
    """Add default security settings to AdminSettings table"""
    with app.app_context():
        settings = [
            {
                'setting_key': 'login_max_attempts',
                'setting_value': '5',
            },
            {
                'setting_key': 'login_lock_duration_minutes',
                'setting_value': '30',
            },
            {
                'setting_key': 'audit_log_retention_days',
                'setting_value': '365',
            },
        ]
        
        for setting_data in settings:
            # Check if setting already exists
            existing = AdminSettings.query.filter_by(
                setting_key=setting_data['setting_key']
            ).first()
            
            if not existing:
                setting = AdminSettings(**setting_data)
                db.session.add(setting)
                print(f"Added setting: {setting_data['setting_key']} = {setting_data['setting_value']}")
            else:
                print(f"Setting already exists: {setting_data['setting_key']}")
        
        db.session.commit()
        print("Security settings seeded successfully")


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    seed_security_settings(app)
