"""
Integration tests for Capability API endpoints
Tests the actual API endpoints with real database operations
"""
import pytest
import json
from app.models.models import db, McpService, Service, Capability


def test_get_capabilities_for_service_integration(client, db):
    """Test GET /api/apps/<service_id>/capabilities with real database"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Create MCP Service
    mcp_service = McpService(
        name='Integration Test Service',
        identifier='integration-test',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    # Create Service
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Integration Test App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    # Create Capabilities with timeout_seconds
    cap1 = Capability(
        app_id=service.id,
        name='test_capability_1',
        capability_type='tool',
        url='https://api.example.com/test1',
        description='Test capability 1',
        timeout_seconds=60,
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    cap2 = Capability(
        app_id=service.id,
        name='test_capability_2',
        capability_type='prompt',
        url='',
        description='Test capability 2',
        timeout_seconds=45,
        template_content='Test {{variable}}',
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(cap1)
    db.session.add(cap2)
    db.session.commit()
    
    # Call the actual API endpoint
    response = client.get(f'/api/apps/{service.id}/capabilities')
    
    # Verify response
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Check first capability
    cap1_data = next(c for c in data if c['name'] == 'test_capability_1')
    assert cap1_data['timeout_seconds'] == 60
    assert cap1_data['capability_type'] == 'tool'
    assert cap1_data['url'] == 'https://api.example.com/test1'
    assert 'mcp_service_id' in cap1_data
    assert cap1_data['mcp_service_id'] == mcp_service.id
    
    # Check second capability
    cap2_data = next(c for c in data if c['name'] == 'test_capability_2')
    assert cap2_data['timeout_seconds'] == 45
    assert cap2_data['capability_type'] == 'prompt'
    assert cap2_data['template_content'] == 'Test {{variable}}'


def test_get_capabilities_non_existent_service_returns_json_404(client, db):
    """Test that 404 error is returned as JSON, not HTML"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Request capabilities for non-existent service
    response = client.get('/api/apps/999/capabilities')
    
    # Verify 404 response is JSON
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    
    # Verify JSON structure
    data = response.json
    assert 'error' in data
    assert 'not found' in data['error'].lower()
    
    # Ensure response is parseable as JSON (not HTML)
    assert not response.data.decode().startswith('<!doctype')


def test_get_capabilities_nan_service_id_returns_json_404(client, db):
    """Test that /api/apps/NaN/capabilities returns JSON 404, not HTML"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Request capabilities with NaN as service ID (simulates JS parseInt failure)
    response = client.get('/api/apps/NaN/capabilities')
    
    # Verify 404 response is JSON (not HTML)
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    
    # Verify JSON structure
    data = response.json
    assert 'error' in data
    
    # Ensure response is not HTML
    assert not response.data.decode().startswith('<!doctype')


def test_get_capabilities_invalid_string_service_id_returns_json_404(client, db):
    """Test that /api/apps/abc/capabilities returns JSON 404, not HTML"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Request capabilities with string as service ID
    response = client.get('/api/apps/abc/capabilities')
    
    # Verify 404 response is JSON (not HTML)
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    
    # Ensure response is not HTML
    assert not response.data.decode().startswith('<!doctype')


def test_create_capability_via_api_integration(client, db):
    """Test POST /api/apps/<service_id>/capabilities with real database"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Create MCP Service
    mcp_service = McpService(
        name='Create Test Service',
        identifier='create-test',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    # Create Service
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Create Test App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.commit()
    
    # Create capability via API
    response = client.post(f'/api/apps/{service.id}/capabilities', json={
        'name': 'new_capability',
        'capability_type': 'tool',
        'url': 'https://api.example.com/new',
        'description': 'New capability',
        'timeout_seconds': 90,
        'headers': {'Authorization': 'Bearer token'},
        'body_params': {'key': 'value'}
    })
    
    # Verify response
    assert response.status_code == 201
    data = response.json
    
    assert data['name'] == 'new_capability'
    assert data['timeout_seconds'] == 90
    assert data['capability_type'] == 'tool'
    assert data['headers'] == {'Authorization': 'Bearer token'}
    
    # Verify it was saved to database
    saved_cap = Capability.query.filter_by(name='new_capability').first()
    assert saved_cap is not None
    assert saved_cap.timeout_seconds == 90
    
    # Verify GET returns the same data
    get_response = client.get(f'/api/apps/{service.id}/capabilities')
    assert get_response.status_code == 200
    capabilities = get_response.json
    assert len(capabilities) == 1
    assert capabilities[0]['timeout_seconds'] == 90


def test_update_capability_via_api_integration(client, db):
    """Test PUT /api/capabilities/<capability_id> with real database"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Create MCP Service and Service
    mcp_service = McpService(
        name='Update Test Service',
        identifier='update-test',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Update Test App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    # Create capability
    capability = Capability(
        app_id=service.id,
        name='update_test',
        capability_type='tool',
        url='https://api.example.com/old',
        description='Old description',
        timeout_seconds=30,
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(capability)
    db.session.commit()
    
    # Update via API
    response = client.put(f'/api/capabilities/{capability.id}', json={
        'name': 'updated_capability',
        'timeout_seconds': 120,
        'description': 'New description'
    })
    
    # Verify response
    assert response.status_code == 200
    data = response.json
    
    assert data['name'] == 'updated_capability'
    assert data['timeout_seconds'] == 120
    assert data['description'] == 'New description'
    
    # Verify database was updated
    db.session.refresh(capability)
    assert capability.name == 'updated_capability'
    assert capability.timeout_seconds == 120


def test_capability_to_dict_with_service_relationship(db):
    """Test that to_dict() works correctly with service relationship"""
    # Create MCP Service
    mcp_service = McpService(
        name='To Dict Test Service',
        identifier='to-dict-test',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    # Create Service
    service = Service(
        mcp_service_id=mcp_service.id,
        name='To Dict Test App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    # Create capability
    capability = Capability(
        app_id=service.id,
        name='to_dict_test',
        capability_type='tool',
        url='https://api.example.com/test',
        description='Test',
        timeout_seconds=75,
        headers=json.dumps({'Test': 'Header'}),
        body_params=json.dumps({'test': 'param'})
    )
    db.session.add(capability)
    db.session.commit()
    
    # Call to_dict()
    result = capability.to_dict()
    
    # Verify all fields
    assert result['id'] == capability.id
    assert result['name'] == 'to_dict_test'
    assert result['capability_type'] == 'tool'
    assert result['timeout_seconds'] == 75
    assert result['mcp_service_id'] == mcp_service.id
    assert result['headers'] == {'Test': 'Header'}
    assert result['body_params'] == {'test': 'param'}


def test_capability_to_dict_without_service_relationship(db):
    """Test that to_dict() works when service relationship is missing"""
    # Create orphaned capability (no corresponding service)
    capability = Capability(
        app_id=999,  # Non-existent service ID
        name='orphan_capability',
        capability_type='tool',
        url='https://api.example.com/orphan',
        description='Orphan capability',
        timeout_seconds=60,
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(capability)
    db.session.commit()
    
    # Call to_dict() - should not crash
    result = capability.to_dict()
    
    # Verify basic fields
    assert result['id'] == capability.id
    assert result['name'] == 'orphan_capability'
    assert result['timeout_seconds'] == 60
    
    # mcp_service_id should not be in result (service doesn't exist)
    assert 'mcp_service_id' not in result or result.get('mcp_service_id') is None
    
    # Clean up
    db.session.delete(capability)
    db.session.commit()


def test_invalid_service_id_returns_json_error(client, db):
    """Test that invalid service IDs return JSON error, not HTML"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Test with string "NaN" (simulating JavaScript parseInt failure)
    response = client.get('/api/apps/NaN/capabilities')
    
    # Verify response is JSON, not HTML
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    
    # Verify JSON structure
    data = response.json
    assert 'error' in data
    assert 'path' in data
    assert data['path'] == '/api/apps/NaN/capabilities'
    
    # Ensure it's not HTML
    assert not response.data.decode().startswith('<!doctype')
    assert not response.data.decode().startswith('<html')


def test_invalid_service_id_zero_returns_json_error(client, db):
    """Test that service ID 0 returns JSON error"""
    # Login
    client.post('/login', data={
        'username': 'accel',
        'password': 'universe'
    })
    
    # Test with 0 (invalid ID)
    response = client.get('/api/apps/0/capabilities')
    
    # Verify response is JSON
    assert response.status_code == 404
    assert response.content_type == 'application/json'
    
    data = response.json
    assert 'error' in data
