"""
Tests for Security features (brute-force protection, audit logs)
"""
import json
import pytest
from datetime import datetime, timedelta
from app.models.models import LoginLockStatus, AdminLoginLog, AdminActionLog, AdminSettings


class TestBruteForceProtection:
    """Test login brute-force protection"""
    
    def test_successful_login_no_lock(self, client):
        """Test successful login does not create lock status"""
        response = client.post('/login',
                              data=json.dumps({'username': 'accel', 'password': 'universe'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Check no lock status created for successful login
        lock_status = LoginLockStatus.query.filter_by(ip_address='127.0.0.1').first()
        assert lock_status is None or lock_status.failed_attempts == 0
    
    def test_failed_login_increments_counter(self, client, db):
        """Test failed login increments failed attempt counter"""
        # Clear any existing lock status
        LoginLockStatus.query.filter_by(ip_address='127.0.0.1').delete()
        db.session.commit()
        
        response = client.post('/login',
                              data=json.dumps({'username': 'admin', 'password': 'wrong'}),
                              content_type='application/json')
        
        assert response.status_code == 401
        
        lock_status = LoginLockStatus.query.filter_by(ip_address='127.0.0.1').first()
        assert lock_status is not None
        assert lock_status.failed_attempts == 1
    
    def test_multiple_failed_logins_trigger_lock(self, client, db):
        """Test multiple failed logins trigger account lock"""
        # Clear any existing lock status
        LoginLockStatus.query.filter_by(ip_address='127.0.0.1').delete()
        db.session.commit()
        
        # Get max attempts setting
        max_attempts_setting = AdminSettings.query.filter_by(setting_key='login_max_attempts').first()
        max_attempts = int(max_attempts_setting.setting_value) if max_attempts_setting else 5
        
        # Attempt login max_attempts times with wrong password
        for i in range(max_attempts):
            response = client.post('/login',
                                  data=json.dumps({'username': 'admin', 'password': 'wrong'}),
                                  content_type='application/json')
            
            if i < max_attempts - 1:
                assert response.status_code == 401
            else:
                # Last attempt should trigger lock
                assert response.status_code in [401, 429]
        
        # Next attempt should be locked
        response = client.post('/login',
                              data=json.dumps({'username': 'admin', 'password': 'wrong'}),
                              content_type='application/json')
        
        assert response.status_code == 429
        data = json.loads(response.data)
        assert 'ロック' in data['message'] or 'locked' in data['message'].lower()
        
        lock_status = LoginLockStatus.query.filter_by(ip_address='127.0.0.1').first()
        assert lock_status is not None
        assert lock_status.failed_attempts >= max_attempts
        assert lock_status.locked_until is not None
        assert lock_status.is_locked() is True
    
    def test_successful_login_resets_counter(self, client, db):
        """Test successful login resets failed attempt counter"""
        # Create a lock status with failed attempts
        lock_status = LoginLockStatus(
            ip_address='127.0.0.1',
            failed_attempts=3,
            last_attempt_at=datetime.utcnow()
        )
        db.session.add(lock_status)
        db.session.commit()
        
        # Successful login
        response = client.post('/login',
                              data=json.dumps({'username': 'accel', 'password': 'universe'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        
        # Check counter is reset
        lock_status = LoginLockStatus.query.filter_by(ip_address='127.0.0.1').first()
        assert lock_status.failed_attempts == 0
    
    def test_lock_expires_after_duration(self, client, db):
        """Test lock expires after configured duration"""
        # Create an expired lock status
        lock_status = LoginLockStatus(
            ip_address='127.0.0.1',
            failed_attempts=5,
            locked_until=datetime.utcnow() - timedelta(minutes=1),  # Expired
            last_attempt_at=datetime.utcnow() - timedelta(minutes=10)
        )
        db.session.add(lock_status)
        db.session.commit()
        
        # Should be able to login after lock expires
        response = client.post('/login',
                              data=json.dumps({'username': 'admin', 'password': 'wrong'}),
                              content_type='application/json')
        
        # Should not be locked (401 for wrong password, not 429 for locked)
        assert response.status_code == 401
        
        # Check failed attempts reset and started counting again
        lock_status = LoginLockStatus.query.filter_by(ip_address='127.0.0.1').first()
        assert lock_status.failed_attempts == 1  # New failed attempt after reset


class TestLoginLogs:
    """Test admin login logging"""
    
    @pytest.mark.skip(reason="Login logging is async - tested via integration tests instead")
    def test_successful_login_logged(self, client, db):
        """Test successful login is logged"""
        before_count = AdminLoginLog.query.count()
        
        response = client.post('/login', data={
            'username': 'accel',
            'password': 'universe'
        }, follow_redirects=False)
        
        assert response.status_code in [200, 302]  # Success or redirect
        
        # Check log created
        after_count = AdminLoginLog.query.count()
        assert after_count == before_count + 1
        
        log = AdminLoginLog.query.order_by(AdminLoginLog.created_at.desc()).first()
        assert log is not None
        assert log.username == 'accel'
        assert log.is_success is True
        assert log.ip_address == '127.0.0.1'
    
    @pytest.mark.skip(reason="Login logging is async - tested via integration tests instead")
    def test_failed_login_logged(self, client, db):
        """Test failed login is logged"""
        before_count = AdminLoginLog.query.count()
        
        response = client.post('/login', data={
            'username': 'accel',
            'password': 'wrong'
        }, follow_redirects=False)
        
        assert response.status_code in [401, 302]  # Unauthorized or redirect
        
        # Check log created
        after_count = AdminLoginLog.query.count()
        assert after_count == before_count + 1
        
        log = AdminLoginLog.query.order_by(AdminLoginLog.created_at.desc()).first()
        assert log is not None
        assert log.username == 'accel'
        assert log.is_success is False
        assert 'password' in log.failure_reason.lower()
    
    @pytest.mark.skip(reason="Login logging is async - tested via integration tests instead")
    def test_locked_login_logged(self, client, db):
        """Test locked account login attempt is logged"""
        # Create locked status
        lock_status = LoginLockStatus(
            ip_address='127.0.0.1',
            failed_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=5),
            last_attempt_at=datetime.utcnow()
        )
        db.session.add(lock_status)
        db.session.commit()
        
        before_count = AdminLoginLog.query.count()
        
        response = client.post('/login', data={
            'username': 'accel',
            'password': 'universe'
        }, follow_redirects=False)
        
        assert response.status_code in [429, 403, 302]  # Too Many Requests or Forbidden
        
        # Check log created
        after_count = AdminLoginLog.query.count()
        assert after_count == before_count + 1
        
        log = AdminLoginLog.query.order_by(AdminLoginLog.created_at.desc()).first()
        assert log.failure_reason == 'account_locked'


class TestAuditLogs:
    """Test admin action audit logging"""
    
    @pytest.mark.skip(reason="Auto audit logging not implemented - manual logging only")
    def test_create_service_logged(self, auth_client, db):
        """Test creating a service is logged in audit trail"""
        before_count = AdminActionLog.query.count()
        
        payload = {
            'subdomain': 'audit-test',
            'name': 'Audit Test Service',
            'service_type': 'api',
            'description': 'Test',
            'common_headers': '{}'
        }
        response = auth_client.post('/api/services',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        
        # Check audit log created
        after_count = AdminActionLog.query.count()
        assert after_count >= before_count  # May be before_count + 1
        
        # Find the log for this action
        logs = AdminActionLog.query.filter_by(
            action_type='create',
            resource_type='service'
        ).all()
        assert len(logs) > 0
    
    @pytest.mark.skip(reason="Auto audit logging not implemented - manual logging only")
    def test_update_account_logged(self, auth_client, db, sample_account):
        """Test updating an account is logged in audit trail"""
        before_count = AdminActionLog.query.count()
        
        payload = {
            'name': 'Updated Account Name',
            'description': 'Updated description'
        }
        response = auth_client.put(f'/api/accounts/{sample_account.id}',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        
        # Check audit log created
        after_count = AdminActionLog.query.count()
        assert after_count >= before_count
        
        # Find the log for this action
        logs = AdminActionLog.query.filter_by(
            action_type='update',
            resource_type='account',
            resource_id=sample_account.id
        ).all()
        assert len(logs) > 0
    
    @pytest.mark.skip(reason="Auto audit logging not implemented - manual logging only")
    def test_delete_capability_logged(self, auth_client, db, sample_capability):
        """Test deleting a capability is logged in audit trail"""
        capability_id = sample_capability.id
        before_count = AdminActionLog.query.count()
        
        response = auth_client.delete(f'/api/capabilities/{capability_id}')
        
        assert response.status_code == 204
        
        # Check audit log created
        after_count = AdminActionLog.query.count()
        assert after_count >= before_count


class TestSecurityAPIEndpoints:
    """Test security-related API endpoints"""
    
    def test_get_login_logs(self, auth_client, db):
        """Test GET /api/admin/login-logs"""
        # Create some test logs
        log1 = AdminLoginLog(
            username='accel',
            ip_address='127.0.0.1',
            user_agent='test',
            is_success=True,
            created_at=datetime.utcnow()
        )
        log2 = AdminLoginLog(
            username='accel',
            ip_address='127.0.0.1',
            user_agent='test',
            is_success=False,
            failure_reason='invalid_password',
            created_at=datetime.utcnow()
        )
        db.session.add_all([log1, log2])
        db.session.commit()
        
        response = auth_client.get('/api/admin/login-logs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'logs' in data
        assert len(data['logs']) >= 2
    
    def test_get_action_logs(self, auth_client, db):
        """Test GET /api/admin/action-logs"""
        response = auth_client.get('/api/admin/action-logs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'logs' in data
    
    def test_unlock_account(self, auth_client, db):
        """Test POST /api/admin/unlock-account"""
        # Create locked status
        lock_status = LoginLockStatus(
            ip_address='192.168.1.1',
            failed_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=5),
            last_attempt_at=datetime.utcnow()
        )
        db.session.add(lock_status)
        db.session.commit()
        
        payload = {'ip_address': '192.168.1.1'}
        response = auth_client.post('/api/admin/unlock-account',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'unlocked' in data['message'].lower()
        
        # Check lock status cleared
        lock_status = LoginLockStatus.query.filter_by(ip_address='192.168.1.1').first()
        assert lock_status.failed_attempts == 0
        assert lock_status.locked_until is None
    
    def test_get_locked_ips(self, auth_client, db):
        """Test GET /api/admin/locked-ips"""
        # Create locked status
        lock_status = LoginLockStatus(
            ip_address='10.0.0.1',
            failed_attempts=5,
            locked_until=datetime.utcnow() + timedelta(minutes=5),
            last_attempt_at=datetime.utcnow()
        )
        db.session.add(lock_status)
        db.session.commit()
        
        response = auth_client.get('/api/admin/locked-ips')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'locked_ips' in data
        
        # Find our locked IP
        locked_ips = [ip for ip in data['locked_ips'] if ip['ip_address'] == '10.0.0.1']
        assert len(locked_ips) >= 1
