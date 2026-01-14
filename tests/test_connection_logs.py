"""
Tests for MCP Connection Logs
接続ログの記録・取得・分析機能のテスト
"""
import pytest
from datetime import datetime, timedelta, UTC
from app.models.models import McpConnectionLog, McpService, Service, Capability, ConnectionAccount


class TestMcpConnectionLogModel:
    """McpConnectionLog モデルの基本テスト"""
    
    def test_create_connection_log_success(self, db, sample_account, sample_service, sample_capability):
        """成功した接続ログの作成テスト"""
        mcp_service = McpService(
            identifier='test-mcp',
            name='Test MCP Service',
            routing_type='subdomain',
            access_control='restricted'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        log = McpConnectionLog(
            account_id=sample_account.id,
            account_name=sample_account.name,
            mcp_service_id=mcp_service.id,
            mcp_service_name=mcp_service.name,
            app_id=sample_service.id,
            app_name=sample_service.name,
            capability_id=sample_capability.id,
            capability_name=sample_capability.name,
            mcp_method='tools/call',
            tool_name='test_tool',
            request_id='req-123',
            status_code=200,
            is_success=True,
            ip_address='192.168.1.100',
            user_agent='MCP Client/1.0',
            access_control='restricted',
            duration_ms=150
        )
        db.session.add(log)
        db.session.commit()
        
        assert log.id is not None
        assert log.account_id == sample_account.id
        assert log.mcp_method == 'tools/call'
        assert log.is_success is True
        assert log.duration_ms == 150
    
    def test_create_connection_log_failure(self, db):
        """失敗した接続ログの作成テスト"""
        log = McpConnectionLog(
            mcp_method='tools/call',
            tool_name='non_existent_tool',
            request_id='req-456',
            status_code=404,
            is_success=False,
            error_code=-32601,
            error_message='Method not found',
            ip_address='192.168.1.101',
            access_control='public'
        )
        db.session.add(log)
        db.session.commit()
        
        assert log.id is not None
        assert log.is_success is False
        assert log.error_code == -32601
        assert log.error_message == 'Method not found'
    
    def test_connection_log_to_dict(self, db, sample_account):
        """to_dict メソッドのテスト"""
        log = McpConnectionLog(
            account_id=sample_account.id,
            account_name=sample_account.name,
            mcp_method='initialize',
            request_id='req-789',
            status_code=200,
            is_success=True,
            ip_address='192.168.1.102',
            request_body='{"method": "initialize"}',
            response_body='{"result": "ok"}',
            duration_ms=50
        )
        db.session.add(log)
        db.session.commit()
        
        # Without bodies
        data = log.to_dict(include_bodies=False)
        assert data['id'] == log.id
        assert data['account_name'] == sample_account.name
        assert data['mcp_method'] == 'initialize'
        assert data['is_success'] is True
        assert 'request_body' not in data
        assert 'response_body' not in data
        
        # With bodies
        data_with_bodies = log.to_dict(include_bodies=True)
        assert data_with_bodies['request_body'] == '{"method": "initialize"}'
        assert data_with_bodies['response_body'] == '{"result": "ok"}'
    
    def test_public_access_log(self, db):
        """パブリックアクセスのログ（account_idなし）"""
        log = McpConnectionLog(
            account_id=None,
            account_name=None,
            mcp_method='tools/list',
            request_id='req-public',
            status_code=200,
            is_success=True,
            ip_address='203.0.113.1',
            access_control='public'
        )
        db.session.add(log)
        db.session.commit()
        
        assert log.id is not None
        assert log.account_id is None
        assert log.access_control == 'public'


class TestConnectionLogAPI:
    """接続ログAPI のテスト"""
    
    def test_get_connection_logs(self, auth_client, db, sample_account):
        """接続ログ一覧取得"""
        # Create test logs
        for i in range(3):
            log = McpConnectionLog(
                account_id=sample_account.id,
                account_name=sample_account.name,
                mcp_method='tools/call',
                tool_name=f'tool_{i}',
                request_id=f'req-{i}',
                status_code=200,
                is_success=True,
                ip_address='192.168.1.100'
            )
            db.session.add(log)
        db.session.commit()
        
        response = auth_client.get('/api/connection-logs')
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) >= 3
    
    def test_get_connection_logs_filtered_by_account(self, auth_client, db, sample_account):
        """アカウント別フィルタリング"""
        # Create logs for different accounts
        import secrets
        account2 = ConnectionAccount(
            name='Account 2',
            bearer_token=f'test_token_{secrets.token_hex(16)}'
        )
        db.session.add(account2)
        db.session.commit()
        
        log1 = McpConnectionLog(
            account_id=sample_account.id,
            account_name=sample_account.name,
            mcp_method='tools/call',
            request_id='req-1',
            status_code=200,
            is_success=True
        )
        log2 = McpConnectionLog(
            account_id=account2.id,
            account_name=account2.name,
            mcp_method='tools/call',
            request_id='req-2',
            status_code=200,
            is_success=True
        )
        db.session.add_all([log1, log2])
        db.session.commit()
        
        response = auth_client.get(f'/api/connection-logs?account_id={sample_account.id}')
        assert response.status_code == 200
        data = response.get_json()
        logs = data['items']
        assert all(log['account_id'] == sample_account.id for log in logs if log.get('account_id'))
    
    def test_get_connection_logs_filtered_by_success(self, auth_client, db):
        """成功/失敗でフィルタリング"""
        log_success = McpConnectionLog(
            mcp_method='tools/call',
            request_id='req-success',
            status_code=200,
            is_success=True
        )
        log_failure = McpConnectionLog(
            mcp_method='tools/call',
            request_id='req-failure',
            status_code=500,
            is_success=False,
            error_message='Internal error'
        )
        db.session.add_all([log_success, log_failure])
        db.session.commit()
        
        # Filter by success
        response = auth_client.get('/api/connection-logs?is_success=true')
        assert response.status_code == 200
        data = response.get_json()
        assert all(log['is_success'] for log in data['items'])
        
        # Filter by failure
        response = auth_client.get('/api/connection-logs?is_success=false')
        assert response.status_code == 200
        data = response.get_json()
        assert all(not log['is_success'] for log in data['items'])
    
    def test_get_connection_log_detail(self, auth_client, db, sample_account):
        """接続ログ詳細取得"""
        log = McpConnectionLog(
            account_id=sample_account.id,
            account_name=sample_account.name,
            mcp_method='tools/call',
            tool_name='test_tool',
            request_id='req-detail',
            status_code=200,
            is_success=True,
            request_body='{"method": "tools/call", "params": {"name": "test_tool"}}',
            response_body='{"result": "success"}',
            duration_ms=200
        )
        db.session.add(log)
        db.session.commit()
        
        response = auth_client.get(f'/api/connection-logs/{log.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == log.id
        assert data['tool_name'] == 'test_tool'
        assert data['duration_ms'] == 200
        # Bodies should be included in detail view
        assert 'request_body' in data
        assert 'response_body' in data


class TestConnectionLogStatistics:
    """接続ログ統計のテスト"""
    
    def test_connection_log_statistics(self, auth_client, db, sample_account):
        """接続ログ統計の取得"""
        # Create test data
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Success logs
        for i in range(5):
            log = McpConnectionLog(
                account_id=sample_account.id,
                mcp_method='tools/call',
                request_id=f'req-success-{i}',
                status_code=200,
                is_success=True,
                created_at=now - timedelta(hours=i),
                duration_ms=100 + i * 10
            )
            db.session.add(log)
        
        # Failure logs
        for i in range(2):
            log = McpConnectionLog(
                account_id=sample_account.id,
                mcp_method='tools/call',
                request_id=f'req-failure-{i}',
                status_code=500,
                is_success=False,
                created_at=now - timedelta(hours=i),
                error_message='Error'
            )
            db.session.add(log)
        
        db.session.commit()
        
        response = auth_client.get('/api/connection-logs/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total' in data
        assert 'success' in data
        assert 'error' in data
        assert 'last_24h' in data
        assert 'by_method' in data
        assert data['total'] >= 7
        assert data['success'] >= 5
        assert data['error'] >= 2


class TestConnectionLogRetention:
    """接続ログの保持期間テスト"""
    
    def test_old_logs_cleanup(self, auth_client, db):
        """古いログの削除"""
        now = datetime.now(UTC).replace(tzinfo=None)
        
        # Old log (91 days ago)
        old_log = McpConnectionLog(
            mcp_method='tools/call',
            request_id='req-old',
            status_code=200,
            is_success=True,
            created_at=now - timedelta(days=91)
        )
        
        # Recent log
        recent_log = McpConnectionLog(
            mcp_method='tools/call',
            request_id='req-recent',
            status_code=200,
            is_success=True,
            created_at=now - timedelta(days=1)
        )
        
        db.session.add_all([old_log, recent_log])
        db.session.commit()
        
        old_log_id = old_log.id
        recent_log_id = recent_log.id
        
        # Cleanup old logs (retention: 90 days)
        response = auth_client.delete('/api/connection-logs/cleanup', json={
            'retention_days': 90
        })
        assert response.status_code == 200
        
        # Check old log is deleted
        assert db.session.get(McpConnectionLog, old_log_id) is None
        # Check recent log still exists
        assert db.session.get(McpConnectionLog, recent_log_id) is not None
