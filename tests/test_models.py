"""
Tests for database models
"""
import pytest
from app.models.models import (
    Service, Capability, ConnectionAccount, AccountPermission,
    McpServiceTemplate, McpCapabilityTemplate
)


class TestServiceModel:
    """Test Service model"""
    
    def test_create_service(self, db):
        """Test creating a service"""
        service = Service(
            subdomain='test',
            name='Test Service',
            service_type='api',
            description='Test description'
        )
        db.session.add(service)
        db.session.commit()
        
        assert service.id is not None
        assert service.subdomain == 'test'
        assert service.name == 'Test Service'
        assert service.service_type == 'api'
    
    def test_service_to_dict(self, sample_service):
        """Test service to_dict method"""
        data = sample_service.to_dict()
        
        assert data['subdomain'] == 'test-service'
        assert data['name'] == 'Test Service'
        assert data['service_type'] == 'api'
        assert 'id' in data
        assert 'created_at' in data
    
    def test_service_mcp_url(self, db):
        """Test MCP service with mcp_url"""
        service = Service(
            subdomain='mcp-test',
            name='MCP Service',
            service_type='mcp',
            mcp_url='http://localhost:3000/mcp'
        )
        db.session.add(service)
        db.session.commit()
        
        assert service.mcp_url == 'http://localhost:3000/mcp'


class TestCapabilityModel:
    """Test Capability model"""
    
    def test_create_capability(self, db, sample_service):
        """Test creating a capability"""
        capability = Capability(
            service_id=sample_service.id,
            name='test_cap',
            capability_type='tool',
            url='https://api.example.com/test',
            is_enabled=True
        )
        db.session.add(capability)
        db.session.commit()
        
        assert capability.id is not None
        assert capability.name == 'test_cap'
        assert capability.is_enabled is True
    
    def test_capability_to_dict(self, sample_capability):
        """Test capability to_dict method"""
        data = sample_capability.to_dict()
        
        assert data['name'] == 'test_capability'
        assert data['capability_type'] == 'tool'
        assert data['is_enabled'] is True
        assert 'service_id' in data
    
    def test_capability_relationship(self, sample_capability, sample_service):
        """Test capability-service relationship"""
        assert sample_capability.service_id == sample_service.id
    
    def test_toggle_capability(self, db, sample_capability):
        """Test toggling capability enabled state"""
        original_state = sample_capability.is_enabled
        sample_capability.is_enabled = not original_state
        db.session.commit()
        
        assert sample_capability.is_enabled != original_state


class TestConnectionAccountModel:
    """Test ConnectionAccount model"""
    
    def test_create_account(self, db):
        """Test creating a connection account"""
        account = ConnectionAccount(
            name='Test Account',
            bearer_token='test_token_456',
            notes='Test notes'
        )
        db.session.add(account)
        db.session.commit()
        
        assert account.id is not None
        assert account.name == 'Test Account'
        assert account.bearer_token is not None
    
    def test_account_bearer_token_generated(self, sample_account):
        """Test bearer token is auto-generated"""
        assert sample_account.bearer_token is not None
        assert len(sample_account.bearer_token) > 0
    
    def test_account_to_dict(self, sample_account):
        """Test account to_dict method"""
        data = sample_account.to_dict()
        
        assert data['name'] == 'Test Account'
        assert 'bearer_token' in data
        assert 'id' in data


class TestAccountPermissionModel:
    """Test AccountPermission model"""
    
    def test_create_permission(self, db, sample_account, sample_capability):
        """Test creating an account permission"""
        permission = AccountPermission(
            account_id=sample_account.id,
            capability_id=sample_capability.id
        )
        db.session.add(permission)
        db.session.commit()
        
        assert permission.id is not None
        assert permission.account_id == sample_account.id
        assert permission.capability_id == sample_capability.id
    
    def test_permission_to_dict(self, db, sample_account, sample_capability):
        """Test permission to_dict method"""
        permission = AccountPermission(
            account_id=sample_account.id,
            capability_id=sample_capability.id
        )
        db.session.add(permission)
        db.session.commit()
        
        data = permission.to_dict()
        assert data['account_id'] == sample_account.id
        assert data['capability_id'] == sample_capability.id


class TestMcpServiceTemplateModel:
    """Test McpServiceTemplate model"""
    
    def test_create_template(self, db):
        """Test creating a service template"""
        template = McpServiceTemplate(
            name='Test Template',
            template_type='custom',
            service_type='api',
            description='Test template',
            common_headers='{}',
            icon='🧪',
            category='Test'
        )
        db.session.add(template)
        db.session.commit()
        
        assert template.id is not None
        assert template.name == 'Test Template'
        assert template.template_type == 'custom'
    
    def test_template_to_dict(self, sample_template):
        """Test template to_dict method"""
        data = sample_template.to_dict()
        
        assert data['name'] == 'Test Template'
        assert data['template_type'] == 'custom'
        assert data['icon'] == '🧪'
        
        # to_export_dictにはcapabilitiesが含まれる
        export_data = sample_template.to_export_dict()
        assert 'capabilities' in export_data


class TestMcpCapabilityTemplateModel:
    """Test McpCapabilityTemplate model"""
    
    def test_create_capability_template(self, db, sample_template):
        """Test creating a capability template"""
        cap_template = McpCapabilityTemplate(
            service_template_id=sample_template.id,
            name='test_cap_template',
            capability_type='tool',
            url='https://api.example.com/test'
        )
        db.session.add(cap_template)
        db.session.commit()
        
        assert cap_template.id is not None
        assert cap_template.name == 'test_cap_template'
    
    def test_capability_template_to_dict(self, sample_capability_template):
        """Test capability template to_dict method"""
        data = sample_capability_template.to_dict()
        
        assert data['name'] == 'test_template_capability'
        assert data['capability_type'] == 'tool'
        assert 'service_template_id' in data
