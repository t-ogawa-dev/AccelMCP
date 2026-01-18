"""
Tests for capability test execution feature
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from app.models.models import (
    db, McpService, Service, Capability, ConnectionAccount
)


@pytest.fixture
def test_capability(db):
    """Create test capability"""
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
    
    # Create Capability
    capability = Capability(
        app_id=service.id,
        name='test_api',
        capability_type='tool',
        url='https://api.example.com/test',
        description='Test API endpoint',
        timeout_seconds=30,
        headers=json.dumps({'Content-Type': 'application/json'}),
        body_params=json.dumps({
            'properties': {
                'query': {'type': 'string', 'description': 'Search query'}
            }
        })
    )
    db.session.add(capability)
    db.session.commit()
    
    return capability


def test_test_execution_endpoint_exists(client, db, test_capability):
    """Test that test execution endpoint exists"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Test endpoint should accept POST
    response = client.post(f'/api/capabilities/{test_capability.id}/test',
        json={'params': {}}
    )
    
    # Should not return 404
    assert response.status_code != 404


@patch('app.services.mcp_handler.httpx.post')
def test_test_execution_success(mock_post, client, db, test_capability):
    """Test successful capability execution"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers.get.return_value = 'application/json'
    mock_response.json.return_value = {'result': 'success', 'data': 'test data'}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Execute test
    response = client.post(f'/api/capabilities/{test_capability.id}/test',
        json={'params': {'query': 'test'}}
    )
    
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert data['status_code'] == 200
    assert 'data' in data


@patch('app.services.mcp_handler.httpx.post')
def test_test_execution_timeout_error(mock_post, client, db, test_capability):
    """Test capability execution with timeout error"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Mock timeout exception
    import httpx
    mock_post.side_effect = httpx.TimeoutException('Request timeout')
    
    # Execute test
    response = client.post(f'/api/capabilities/{test_capability.id}/test',
        json={'params': {}}
    )
    
    assert response.status_code == 500
    data = response.json
    assert data['success'] is False
    assert 'error' in data
    assert 'code' in data['error']


@patch('app.services.mcp_handler.httpx.post')
def test_test_execution_http_error(mock_post, client, db, test_capability):
    """Test capability execution with HTTP error"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Mock HTTP error
    import httpx
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.reason_phrase = 'Not Found'
    mock_response.text = 'Resource not found'
    
    mock_post.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        'Not Found', request=MagicMock(), response=mock_response
    )
    
    # Execute test
    response = client.post(f'/api/capabilities/{test_capability.id}/test',
        json={'params': {}}
    )
    
    assert response.status_code == 500
    data = response.json
    assert data['success'] is False
    assert 'error' in data


def test_test_execution_invalid_capability_id(client, db):
    """Test execution with invalid capability ID"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Try to test non-existent capability
    response = client.post('/api/capabilities/99999/test',
        json={'params': {}}
    )
    
    assert response.status_code == 404


def test_test_execution_requires_login(client, db, test_capability):
    """Test that test execution requires authentication"""
    # Try without login
    response = client.post(f'/api/capabilities/{test_capability.id}/test',
        json={'params': {}}
    )
    
    assert response.status_code == 302  # Redirect to login


def test_test_execution_empty_params(client, db, test_capability):
    """Test execution with empty parameters"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Execute without params
    response = client.post(f'/api/capabilities/{test_capability.id}/test',
        json={}
    )
    
    # Should handle gracefully
    assert response.status_code in [200, 500]


@patch('app.services.mcp_handler.httpx.post')
def test_test_execution_uses_capability_timeout(mock_post, client, db):
    """Test that execution uses capability's timeout setting"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Create capability with custom timeout
    mcp_service = McpService(
        name='Test Service',
        identifier='test',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Test App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    capability = Capability(
        app_id=service.id,
        name='slow_api',
        capability_type='tool',
        url='https://api.example.com/slow',
        description='Slow API',
        timeout_seconds=120,
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(capability)
    db.session.commit()
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers.get.return_value = 'application/json'
    mock_response.json.return_value = {'result': 'ok'}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Execute test
    response = client.post(f'/api/capabilities/{capability.id}/test',
        json={'params': {}}
    )
    
    # Verify timeout was used in httpx call
    assert mock_post.called
    call_kwargs = mock_post.call_args[1]
    assert 'timeout' in call_kwargs
    assert call_kwargs['timeout'] == 120.0
