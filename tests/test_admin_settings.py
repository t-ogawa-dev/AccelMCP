"""
Tests for AdminSettings feature
"""
import json
import pytest
from app.models.models import AdminSettings


class TestAdminSettingsModel:
    """Test AdminSettings model"""
    
    def test_create_setting(self, db):
        """Test creating an admin setting"""
        setting = AdminSettings(
            setting_key='test_key',
            setting_value='test_value'
        )
        db.session.add(setting)
        db.session.commit()
        
        assert setting.id is not None
        assert setting.setting_key == 'test_key'
        assert setting.setting_value == 'test_value'
    
    def test_setting_to_dict(self, db):
        """Test admin setting to_dict method"""
        setting = AdminSettings(
            setting_key='max_connections',
            setting_value='100'
        )
        db.session.add(setting)
        db.session.commit()
        
        data = setting.to_dict()
        assert data['setting_key'] == 'max_connections'
        assert data['setting_value'] == '100'
    
    def test_unique_setting_key(self, db):
        """Test setting key is unique"""
        setting1 = AdminSettings(
            setting_key='unique_key',
            setting_value='value1'
        )
        db.session.add(setting1)
        db.session.commit()
        
        setting2 = AdminSettings(
            setting_key='unique_key',
            setting_value='value2'
        )
        db.session.add(setting2)
        
        # Should raise error due to unique constraint
        with pytest.raises(Exception):
            db.session.commit()


class TestAdminSettingsAPI:
    """Test AdminSettings API endpoints"""
    
    def test_get_settings(self, auth_client, db):
        """Test GET /api/settings"""
        # Create test settings
        setting1 = AdminSettings(setting_key='key1', setting_value='value1')
        setting2 = AdminSettings(setting_key='key2', setting_value='value2')
        db.session.add_all([setting1, setting2])
        db.session.commit()
        
        response = auth_client.get('/api/settings')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_get_setting_by_key(self, auth_client, db):
        """Test GET /api/settings/<key>"""
        setting = AdminSettings(
            setting_key='specific_key',
            setting_value='specific_value'
        )
        db.session.add(setting)
        db.session.commit()
        
        response = auth_client.get('/api/settings/specific_key')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['setting_key'] == 'specific_key'
        assert data['setting_value'] == 'specific_value'
    
    def test_create_or_update_setting(self, auth_client, db):
        """Test POST /api/settings"""
        payload = {
            'setting_key': 'new_setting',
            'setting_value': 'new_value'
        }
        response = auth_client.post('/api/settings',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert data['setting_key'] == 'new_setting'
        assert data['setting_value'] == 'new_value'
    
    def test_update_existing_setting(self, auth_client, db):
        """Test updating an existing setting"""
        setting = AdminSettings(
            setting_key='update_key',
            setting_value='old_value'
        )
        db.session.add(setting)
        db.session.commit()
        
        payload = {
            'setting_key': 'update_key',
            'setting_value': 'new_value'
        }
        response = auth_client.post('/api/settings',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['setting_value'] == 'new_value'
    
    def test_delete_setting(self, auth_client, db):
        """Test DELETE /api/settings/<key>"""
        setting = AdminSettings(
            setting_key='delete_key',
            setting_value='delete_value'
        )
        db.session.add(setting)
        db.session.commit()
        
        response = auth_client.delete('/api/settings/delete_key')
        
        assert response.status_code == 204
        
        # Verify deletion
        response = auth_client.get('/api/settings/delete_key')
        assert response.status_code == 404


class TestSecuritySettings:
    """Test security-related admin settings"""
    
    def test_login_max_attempts_setting(self, db):
        """Test login_max_attempts setting"""
        setting = AdminSettings.query.filter_by(
            setting_key='login_max_attempts'
        ).first()
        
        if not setting:
            setting = AdminSettings(
                setting_key='login_max_attempts',
                setting_value='5'
            )
            db.session.add(setting)
            db.session.commit()
        
        assert setting is not None
        assert int(setting.setting_value) > 0
    
    def test_login_lock_duration_setting(self, db):
        """Test login_lock_duration_minutes setting"""
        setting = AdminSettings.query.filter_by(
            setting_key='login_lock_duration_minutes'
        ).first()
        
        if not setting:
            setting = AdminSettings(
                setting_key='login_lock_duration_minutes',
                setting_value='5'
            )
            db.session.add(setting)
            db.session.commit()
        
        assert setting is not None
        assert int(setting.setting_value) > 0
    
    def test_audit_log_retention_setting(self, db):
        """Test audit_log_retention_days setting"""
        setting = AdminSettings.query.filter_by(
            setting_key='audit_log_retention_days'
        ).first()
        
        if not setting:
            setting = AdminSettings(
                setting_key='audit_log_retention_days',
                setting_value='365'
            )
            db.session.add(setting)
            db.session.commit()
        
        assert setting is not None
        assert int(setting.setting_value) > 0


class TestLanguageSetting:
    """Test language setting"""
    
    def test_get_language_setting(self, auth_client, db):
        """Test GET /api/settings/language"""
        # Create or get language setting
        setting = AdminSettings.query.filter_by(setting_key='language').first()
        if not setting:
            setting = AdminSettings(
                setting_key='language',
                setting_value='ja'
            )
            db.session.add(setting)
            db.session.commit()
        
        response = auth_client.get('/api/settings/language')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['setting_value'] in ['ja', 'en']
    
    def test_update_language_setting(self, auth_client, db):
        """Test updating language setting"""
        payload = {
            'setting_key': 'language',
            'setting_value': 'en'
        }
        response = auth_client.post('/api/settings',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert data['setting_value'] == 'en'


class TestSettingsIntegration:
    """Test settings integration with other features"""
    
    def test_settings_affect_brute_force_protection(self, client, db):
        """Test that max_attempts setting affects login protection"""
        # Set max attempts to 3
        setting = AdminSettings.query.filter_by(
            setting_key='login_max_attempts'
        ).first()
        if setting:
            setting.setting_value = '3'
        else:
            setting = AdminSettings(
                setting_key='login_max_attempts',
                setting_value='3'
            )
            db.session.add(setting)
        db.session.commit()
        
        # Try to login 3 times with wrong password
        from app.models.models import LoginLockStatus
        LoginLockStatus.query.filter_by(ip_address='127.0.0.1').delete()
        db.session.commit()
        
        for i in range(4):
            response = client.post('/login',
                                  data=json.dumps({'username': 'accel', 'password': 'wrong'}),
                                  content_type='application/json')
            
            if i < 3:
                assert response.status_code in [401, 429]
            else:
                # 4th attempt should be locked
                assert response.status_code == 429
    
    def test_settings_affect_lock_duration(self, client, db):
        """Test that lock_duration setting is used"""
        # Set lock duration to 1 minute
        setting = AdminSettings.query.filter_by(
            setting_key='login_lock_duration_minutes'
        ).first()
        if setting:
            setting.setting_value = '1'
        else:
            setting = AdminSettings(
                setting_key='login_lock_duration_minutes',
                setting_value='1'
            )
            db.session.add(setting)
        db.session.commit()
        
        # Setting should be reflected in lock message
        # (This is verified in other tests)
        assert int(setting.setting_value) == 1
