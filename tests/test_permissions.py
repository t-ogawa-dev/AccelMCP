"""
Tests for Account Permissions API
階層的アクセス制御・権限付与/剥奪のテスト
"""
import pytest
from app.models.models import AccountPermission, ConnectionAccount, McpService, Service, Capability


class TestAccountPermissionAPI:
    """Account Permission API のテスト"""
    
    def test_get_account_permissions(self, auth_client, db, sample_account, sample_capability):
        """アカウントの権限一覧取得"""
        permission = AccountPermission(
            account_id=sample_account.id,
            capability_id=sample_capability.id
        )
        db.session.add(permission)
        db.session.commit()
        
        response = auth_client.get(f'/api/accounts/{sample_account.id}/permissions')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p['capability_id'] == sample_capability.id for p in data)
    
    def test_grant_capability_permission(self, auth_client, db, sample_account, sample_capability):
        """Capability レベルの権限付与"""
        response = auth_client.post(
            f'/api/accounts/{sample_account.id}/permissions',
            json={'capability_id': sample_capability.id}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['account_id'] == sample_account.id
        assert data['capability_id'] == sample_capability.id
        
        # Verify in database
        permission = AccountPermission.query.filter_by(
            account_id=sample_account.id,
            capability_id=sample_capability.id
        ).first()
        assert permission is not None
    
    def test_grant_app_permission(self, auth_client, db, sample_account, sample_service):
        """実装部分 (Service) レベルの権限付与"""
        response = auth_client.post(
            f'/api/accounts/{sample_account.id}/permissions',
            json={'app_id': sample_service.id}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['account_id'] == sample_account.id
        assert data['app_id'] == sample_service.id
        # capability_idは該当レベルでないのでto_dict()に含まれない
        assert 'capability_id' not in data
    
    def test_grant_mcp_service_permission(self, auth_client, db, sample_account):
        """MCP Service レベルの権限付与"""
        mcp_service = McpService(
            identifier='test-mcp',
            name='Test MCP Service',
            routing_type='subdomain',
            access_control='restricted'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        response = auth_client.post(
            f'/api/accounts/{sample_account.id}/permissions',
            json={'mcp_service_id': mcp_service.id}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['account_id'] == sample_account.id
        assert data['mcp_service_id'] == mcp_service.id
        # app_idとcapability_idは該当レベルでないのでto_dict()に含まれない
        assert 'app_id' not in data
        assert 'capability_id' not in data
    
    def test_grant_permission_invalid_multiple_levels(self, auth_client, db, sample_account, sample_service, sample_capability):
        """複数レベル同時指定はエラー"""
        response = auth_client.post(
            f'/api/accounts/{sample_account.id}/permissions',
            json={
                'app_id': sample_service.id,
                'capability_id': sample_capability.id
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_grant_permission_invalid_no_level(self, auth_client, db, sample_account):
        """レベル未指定はエラー"""
        response = auth_client.post(
            f'/api/accounts/{sample_account.id}/permissions',
            json={}
        )
        assert response.status_code == 400
    
    def test_grant_duplicate_permission(self, auth_client, db, sample_account, sample_capability):
        """重複権限付与はエラー"""
        # First grant
        permission = AccountPermission(
            account_id=sample_account.id,
            capability_id=sample_capability.id
        )
        db.session.add(permission)
        db.session.commit()
        
        # Try to grant again
        response = auth_client.post(
            f'/api/accounts/{sample_account.id}/permissions',
            json={'capability_id': sample_capability.id}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert '既に付与されています' in data['error']
    
    def test_revoke_permission(self, auth_client, db, sample_account, sample_capability):
        """権限剥奪"""
        permission = AccountPermission(
            account_id=sample_account.id,
            capability_id=sample_capability.id
        )
        db.session.add(permission)
        db.session.commit()
        permission_id = permission.id
        
        response = auth_client.delete(f'/api/permissions/{permission_id}')
        assert response.status_code == 204
        
        # Verify deleted
        deleted_permission = db.session.get(AccountPermission, permission_id)
        assert deleted_permission is None


class TestCapabilityPermissionsAPI:
    """Capability別権限管理APIのテスト"""
    
    def test_get_capability_permissions(self, auth_client, db, sample_capability):
        """Capabilityの権限設定取得"""
        # Create accounts
        import secrets
        account1 = ConnectionAccount(
            name='Account 1',
            bearer_token=f'test_token_{secrets.token_hex(16)}'
        )
        account2 = ConnectionAccount(
            name='Account 2',
            bearer_token=f'test_token_{secrets.token_hex(16)}'
        )
        db.session.add_all([account1, account2])
        db.session.commit()
        
        # Grant permission to account1
        permission = AccountPermission(
            account_id=account1.id,
            capability_id=sample_capability.id
        )
        db.session.add(permission)
        db.session.commit()
        
        response = auth_client.get(f'/api/capabilities/{sample_capability.id}/permissions')
        assert response.status_code == 200
        data = response.get_json()
        assert 'enabled' in data
        assert 'disabled' in data
        assert any(acc['id'] == account1.id for acc in data['enabled'])
        assert any(acc['id'] == account2.id for acc in data['disabled'])
    
    def test_update_capability_permissions(self, auth_client, db, sample_capability):
        """Capability権限の一括更新"""
        import secrets
        account1 = ConnectionAccount(
            name='Account 1',
            bearer_token=f'test_token_{secrets.token_hex(16)}'
        )
        account2 = ConnectionAccount(
            name='Account 2',
            bearer_token=f'test_token_{secrets.token_hex(16)}'
        )
        account3 = ConnectionAccount(
            name='Account 3',
            bearer_token=f'test_token_{secrets.token_hex(16)}'
        )
        db.session.add_all([account1, account2, account3])
        db.session.commit()
        
        # Initially grant to account1
        permission = AccountPermission(
            account_id=account1.id,
            capability_id=sample_capability.id
        )
        db.session.add(permission)
        db.session.commit()
        
        # Update: grant to account2 and account3, revoke from account1
        response = auth_client.put(
            f'/api/capabilities/{sample_capability.id}/permissions',
            json={'account_ids': [account2.id, account3.id]}
        )
        assert response.status_code == 200
        
        # Verify
        permissions = AccountPermission.query.filter_by(
            capability_id=sample_capability.id
        ).all()
        account_ids = [p.account_id for p in permissions]
        assert account1.id not in account_ids
        assert account2.id in account_ids
        assert account3.id in account_ids


class TestMcpServicePermissionsAPI:
    """MCP Service別権限管理APIのテスト"""
    
    def test_get_mcp_service_permissions(self, auth_client, db, sample_account):
        """MCP Serviceの権限一覧取得"""
        mcp_service = McpService(
            identifier='test-mcp',
            name='Test MCP',
            routing_type='subdomain',
            access_control='restricted'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        permission = AccountPermission(
            account_id=sample_account.id,
            mcp_service_id=mcp_service.id
        )
        db.session.add(permission)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-services/{mcp_service.id}/permissions')
        assert response.status_code == 200
        data = response.get_json()
        assert 'enabled' in data
        assert 'disabled' in data
        assert isinstance(data['enabled'], list)
        assert len(data['enabled']) >= 1
    
    def test_grant_mcp_service_permission_via_service_endpoint(self, auth_client, db, sample_account):
        """MCP Service endpoint経由での権限付与"""
        mcp_service = McpService(
            identifier='test-mcp-2',
            name='Test MCP 2',
            routing_type='subdomain',
            access_control='restricted'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        response = auth_client.post(
            f'/api/mcp-services/{mcp_service.id}/permissions',
            json={'account_ids': [sample_account.id]}
        )
        assert response.status_code == 200
        
        # Verify
        permission = AccountPermission.query.filter_by(
            account_id=sample_account.id,
            mcp_service_id=mcp_service.id
        ).first()
        assert permission is not None


class TestAppPermissionsAPI:
    """App (Service)別権限管理APIのテスト"""
    
    def test_get_app_permissions(self, auth_client, db, sample_service, sample_account):
        """Appの権限一覧取得"""
        permission = AccountPermission(
            account_id=sample_account.id,
            app_id=sample_service.id
        )
        db.session.add(permission)
        db.session.commit()
        
        response = auth_client.get(f'/api/apps/{sample_service.id}/permissions')
        assert response.status_code == 200
        data = response.get_json()
        assert 'enabled' in data
        assert 'disabled' in data
        assert isinstance(data['enabled'], list)
        assert len(data['enabled']) >= 1
    
    def test_grant_app_permission_via_app_endpoint(self, auth_client, db, sample_service, sample_account):
        """App endpoint経由での権限付与"""
        response = auth_client.post(
            f'/api/apps/{sample_service.id}/permissions',
            json={'account_ids': [sample_account.id]}
        )
        assert response.status_code == 200
        
        permission = AccountPermission.query.filter_by(
            account_id=sample_account.id,
            app_id=sample_service.id
        ).first()
        assert permission is not None


class TestHierarchicalPermissions:
    """階層的アクセス制御のテスト"""
    
    def test_account_permissions_by_level(self, auth_client, db, sample_account, sample_service, sample_capability):
        """レベル別権限取得"""
        mcp_service = McpService(
            identifier='test-mcp',
            name='Test MCP',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Grant different levels
        perm_mcp = AccountPermission(
            account_id=sample_account.id,
            mcp_service_id=mcp_service.id
        )
        perm_app = AccountPermission(
            account_id=sample_account.id,
            app_id=sample_service.id
        )
        perm_cap = AccountPermission(
            account_id=sample_account.id,
            capability_id=sample_capability.id
        )
        db.session.add_all([perm_mcp, perm_app, perm_cap])
        db.session.commit()
        
        response = auth_client.get(f'/api/accounts/{sample_account.id}/permissions/by-level')
        assert response.status_code == 200
        data = response.get_json()
        assert 'mcp_service' in data
        assert 'app' in data
        assert 'capability' in data
        assert len(data['mcp_service']) >= 1
        assert len(data['app']) >= 1
        assert len(data['capability']) >= 1
    
    def test_permission_inheritance(self, auth_client, db, sample_account, sample_service, sample_capability):
        """権限継承のテスト（App権限があればCapabilityアクセス可能）"""
        # Grant app-level permission
        permission = AccountPermission(
            account_id=sample_account.id,
            app_id=sample_service.id
        )
        db.session.add(permission)
        db.session.commit()
        
        # Check if capability (child of app) is accessible
        # This would be tested in integration tests with actual MCP requests
        # Here we just verify the permission structure
        permissions = AccountPermission.query.filter_by(
            account_id=sample_account.id,
            app_id=sample_service.id
        ).all()
        assert len(permissions) == 1
        assert permissions[0].app_id == sample_service.id
        
        # Capability should be accessible via app permission (tested in mcp_controller)
        assert sample_capability.app_id == sample_service.id
