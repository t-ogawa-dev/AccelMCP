"""
Tests for timeout feature
"""
import pytest
import json
from app.models.models import (
    db, McpService, Service, Capability, ConnectionAccount, AccountPermission
)


@pytest.fixture
def test_data(db):
    """Create test data"""
    # Create MCP Service
    mcp_service = McpService(
        name='Test MCP Service',
        identifier='test-mcp',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    # Create Service (App)
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Test App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    # Create Account
    account = ConnectionAccount(
        name='Test Account',
        bearer_token='test_token_123'
    )
    db.session.add(account)
    db.session.flush()
    
    # Create Capabilities with different timeouts
    capability_with_custom_timeout = Capability(
        app_id=service.id,
        name='slow_api',
        capability_type='tool',
        url='https://api.example.com/slow',
        description='A slow API that needs longer timeout',
        timeout_seconds=60,
        headers=json.dumps({'Content-Type': 'application/json'}),
        body_params=json.dumps({})
    )
    
    capability_with_default_timeout = Capability(
        app_id=service.id,
        name='fast_api',
        capability_type='tool',
        url='https://api.example.com/fast',
        description='A fast API with default timeout',
        timeout_seconds=30,
        headers=json.dumps({'Content-Type': 'application/json'}),
        body_params=json.dumps({})
    )
    
    capability_with_no_timeout = Capability(
        app_id=service.id,
        name='no_timeout_api',
        capability_type='tool',
        url='https://api.example.com/no-timeout',
        description='API without explicit timeout',
        timeout_seconds=None,
        headers=json.dumps({'Content-Type': 'application/json'}),
        body_params=json.dumps({})
    )
    
    db.session.add_all([
        capability_with_custom_timeout,
        capability_with_default_timeout,
        capability_with_no_timeout
    ])
    db.session.flush()
    
    # Add permissions
    for cap in [capability_with_custom_timeout, capability_with_default_timeout, capability_with_no_timeout]:
        permission = AccountPermission(
            account_id=account.id,
            capability_id=cap.id
        )
        db.session.add(permission)
    
    db.session.commit()
    
    return {
        'mcp_service': mcp_service,
        'service': service,
        'account': account,
        'capability_with_custom_timeout': capability_with_custom_timeout,
        'capability_with_default_timeout': capability_with_default_timeout,
        'capability_with_no_timeout': capability_with_no_timeout
    }


def test_capability_creation_with_timeout(client, db):
    """Test creating capability with custom timeout"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Create MCP Service and App first
    mcp_response = client.post('/api/mcp-services', 
        json={
            'name': 'Test Service',
            'identifier': 'test-service',
            'routing_type': 'subdomain'
        }
    )
    assert mcp_response.status_code == 201
    mcp_service_id = mcp_response.json['id']
    
    app_response = client.post(f'/api/mcp-services/{mcp_service_id}/apps',
        json={
            'name': 'Test App',
            'service_type': 'api',
            'mcp_url': 'https://api.example.com'
        }
    )
    assert app_response.status_code == 201
    app_id = app_response.json['id']
    
    # Create capability with custom timeout
    response = client.post(f'/api/apps/{app_id}/capabilities',
        json={
            'name': 'test_capability',
            'capability_type': 'tool',
            'url': 'https://api.example.com/test',
            'description': 'Test capability',
            'timeout_seconds': 120,
            'headers': {},
            'body_params': {}
        }
    )
    
    assert response.status_code == 201
    data = response.json
    assert data['timeout_seconds'] == 120


def test_capability_default_timeout(client, db):
    """Test capability uses default timeout when not specified"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Create MCP Service and App
    mcp_response = client.post('/api/mcp-services', 
        json={
            'name': 'Test Service',
            'identifier': 'test-service',
            'routing_type': 'subdomain'
        }
    )
    mcp_service_id = mcp_response.json['id']
    
    app_response = client.post(f'/api/mcp-services/{mcp_service_id}/apps',
        json={
            'name': 'Test App',
            'service_type': 'api',
            'mcp_url': 'https://api.example.com'
        }
    )
    app_id = app_response.json['id']
    
    # Create capability without timeout
    response = client.post(f'/api/apps/{app_id}/capabilities',
        json={
            'name': 'test_capability',
            'capability_type': 'tool',
            'url': 'https://api.example.com/test',
            'description': 'Test capability',
            'headers': {},
            'body_params': {}
        }
    )
    
    assert response.status_code == 201
    data = response.json
    # Should use default value of 30
    assert data['timeout_seconds'] == 30


def test_capability_update_timeout(client, db, test_data):
    """Test updating capability timeout"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    capability = test_data['capability_with_default_timeout']
    
    # Update timeout
    response = client.put(f'/api/capabilities/{capability.id}',
        json={
            'name': capability.name,
            'capability_type': 'tool',
            'url': capability.url,
            'description': capability.description,
            'timeout_seconds': 90,
            'headers': {},
            'body_params': {}
        }
    )
    
    assert response.status_code == 200
    data = response.json
    assert data['timeout_seconds'] == 90


def test_capability_to_dict_includes_timeout(db, test_data):
    """Test that to_dict() includes timeout_seconds"""
    capability = test_data['capability_with_custom_timeout']
    
    result = capability.to_dict()
    
    assert 'timeout_seconds' in result
    assert result['timeout_seconds'] == 60


def test_timeout_validation_min_max(client, db):
    """Test timeout value validation (1-300 seconds)"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Create MCP Service and App
    mcp_response = client.post('/api/mcp-services', 
        json={
            'name': 'Test Service',
            'identifier': 'test-service',
            'routing_type': 'subdomain'
        }
    )
    mcp_service_id = mcp_response.json['id']
    
    app_response = client.post(f'/api/mcp-services/{mcp_service_id}/apps',
        json={
            'name': 'Test App',
            'service_type': 'api',
            'mcp_url': 'https://api.example.com'
        }
    )
    app_id = app_response.json['id']
    
    # Test boundary values
    for timeout in [1, 30, 60, 120, 300]:
        response = client.post(f'/api/apps/{app_id}/capabilities',
            json={
                'name': f'test_capability_{timeout}',
                'capability_type': 'tool',
                'url': 'https://api.example.com/test',
                'description': 'Test capability',
                'timeout_seconds': timeout,
                'headers': {},
                'body_params': {}
            }
        )
        assert response.status_code == 201
        assert response.json['timeout_seconds'] == timeout


def test_null_timeout_defaults_to_30(db, test_data):
    """Test that null timeout returns 30 in to_dict()"""
    capability = test_data['capability_with_no_timeout']
    
    result = capability.to_dict()
    
    assert result['timeout_seconds'] == 30
