"""
Tests for MCP Services feature
"""
import json
import yaml
import pytest
from app.models.models import McpService, Service, Capability


class TestMcpServiceModel:
    """Test McpService model"""
    
    def test_create_mcp_service(self, db):
        """Test creating an MCP service"""
        mcp_service = McpService(
            name='Test MCP Service',
            identifier='test-mcp',
            routing_type='subdomain',
            description='Test MCP service',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        assert mcp_service.id is not None
        assert mcp_service.name == 'Test MCP Service'
        assert mcp_service.identifier == 'test-mcp'
    
    def test_mcp_service_to_dict(self, db):
        """Test mcp_service to_dict method"""
        mcp_service = McpService(
            name='Dict Test',
            identifier='dict-test',
            routing_type='path',
            description='Test',
            is_enabled=False
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        data = mcp_service.to_dict()
        assert data['name'] == 'Dict Test'
        assert data['identifier'] == 'dict-test'
        assert data['routing_type'] == 'path'
        assert data['is_enabled'] is False
    
    def test_mcp_service_with_apps(self, db):
        """Test MCP service with associated apps"""
        mcp_service = McpService(
            name='Service with Apps',
            identifier='service-apps',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create apps associated with this MCP service
        app1 = Service(
            name='App 1',
            service_type='api',
            common_headers='{}',
            mcp_service_id=mcp_service.id
        )
        app2 = Service(
            name='App 2',
            service_type='mcp',
            common_headers='{}',
            mcp_service_id=mcp_service.id
        )
        db.session.add_all([app1, app2])
        db.session.commit()
        
        # Check relationship
        assert len(mcp_service.apps) == 2
        assert app1 in mcp_service.apps
        assert app2 in mcp_service.apps


class TestMcpServiceAPI:
    """Test MCP Service API endpoints"""
    
    def test_get_mcp_services(self, auth_client, db):
        """Test GET /api/mcp-services"""
        # Create test MCP services
        service1 = McpService(name='Service 1', identifier='service1', routing_type='subdomain')
        service2 = McpService(name='Service 2', identifier='service2', routing_type='path')
        db.session.add_all([service1, service2])
        db.session.commit()
        
        response = auth_client.get('/api/mcp-services')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 2
        assert any(s['identifier'] == 'service1' for s in data)
        assert any(s['identifier'] == 'service2' for s in data)
    
    def test_create_mcp_service(self, auth_client):
        """Test POST /api/mcp-services"""
        payload = {
            'name': 'New MCP Service',
            'identifier': 'new-mcp',
            'routing_type': 'subdomain',
            'description': 'A new MCP service'
        }
        response = auth_client.post('/api/mcp-services',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'New MCP Service'
        assert data['identifier'] == 'new-mcp'
        assert data['routing_type'] == 'subdomain'
    
    def test_create_mcp_service_path_routing(self, auth_client):
        """Test creating MCP service with path routing"""
        payload = {
            'name': 'Path Routed Service',
            'identifier': 'path-service',
            'routing_type': 'path',
            'description': 'Uses path routing'
        }
        response = auth_client.post('/api/mcp-services',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['routing_type'] == 'path'
    
    def test_get_mcp_service_detail(self, auth_client, db):
        """Test GET /api/mcp-services/<id>"""
        mcp_service = McpService(
            name='Detail Service',
            identifier='detail-service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-services/{mcp_service.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == mcp_service.id
        assert data['name'] == 'Detail Service'
    
    def test_update_mcp_service(self, auth_client, db):
        """Test PUT /api/mcp-services/<id>"""
        mcp_service = McpService(
            name='Update Service',
            identifier='update-service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        payload = {
            'name': 'Updated MCP Service',
            'description': 'Updated description'
        }
        response = auth_client.put(f'/api/mcp-services/{mcp_service.id}',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated MCP Service'
    
    def test_toggle_mcp_service(self, auth_client, db):
        """Test POST /api/mcp-services/<id>/toggle"""
        mcp_service = McpService(
            name='Toggle Service',
            identifier='toggle-service',
            routing_type='subdomain',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        response = auth_client.post(f'/api/mcp-services/{mcp_service.id}/toggle')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['is_enabled'] is False
        
        # Toggle again
        response = auth_client.post(f'/api/mcp-services/{mcp_service.id}/toggle')
        data = json.loads(response.data)
        assert data['is_enabled'] is True
    
    def test_delete_mcp_service(self, auth_client, db):
        """Test DELETE /api/mcp-services/<id>"""
        mcp_service = McpService(
            name='Delete Service',
            identifier='delete-service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        service_id = mcp_service.id
        
        response = auth_client.delete(f'/api/mcp-services/{service_id}')
        
        assert response.status_code == 204
        
        # Verify deletion
        response = auth_client.get(f'/api/mcp-services/{service_id}')
        assert response.status_code == 404
    
    def test_duplicate_identifier(self, auth_client, db):
        """Test creating MCP service with duplicate identifier fails"""
        # Create first service via API
        payload1 = {
            'name': 'Original',
            'identifier': 'duplicate',
            'routing_type': 'subdomain'
        }
        auth_client.post('/api/mcp-services',
                        data=json.dumps(payload1),
                        content_type='application/json')
        
        # Try to create duplicate
        payload = {
            'name': 'Duplicate',
            'identifier': 'duplicate',
            'routing_type': 'subdomain'
        }
        response = auth_client.post('/api/mcp-services',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code in [400, 409]
    
    def test_export_mcp_service_yaml(self, auth_client, db):
        """Test GET /api/mcp-services/<id>/export - YAML形式でエクスポート"""
        # Create MCP service with apps and capabilities
        mcp_service = McpService(
            name='Export Test Service',
            identifier='export-test',
            routing_type='subdomain',
            description='Service for export testing'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create app
        app = Service(
            mcp_service_id=mcp_service.id,
            name='Test App',
            service_type='api',
            mcp_url='https://api.example.com',
            common_headers='{"Authorization": "Bearer TOKEN"}',
            description='Test app'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create capability
        capability = Capability(
            app_id=app.id,
            name='Test Capability',
            capability_type='tool',
            url='https://api.example.com/test',
            headers='{"Content-Type": "application/json"}',
            body_params='{"param1": "value"}',
            description='Test capability'
        )
        db.session.add(capability)
        db.session.commit()
        
        # Export
        response = auth_client.get(f'/api/mcp-services/{mcp_service.id}/export')
        
        assert response.status_code == 200
        assert 'application/x-yaml' in response.content_type
        assert 'attachment' in response.headers.get('Content-Disposition', '')
        
        # Parse YAML
        data = yaml.safe_load(response.data)
        assert data['name'] == 'Export Test Service'
        assert data['identifier'] == 'export-test'
        assert data['description'] == 'Service for export testing'
        assert len(data['apps']) == 1
        
        app_data = data['apps'][0]
        assert app_data['name'] == 'Test App'
        assert app_data['service_type'] == 'api'
        assert app_data['mcp_url'] == 'https://api.example.com'
        assert 'Authorization' in app_data['common_headers']
        assert len(app_data['capabilities']) == 1
        
        cap_data = app_data['capabilities'][0]
        assert cap_data['name'] == 'Test Capability'
        assert cap_data['capability_type'] == 'tool'
    
    def test_import_mcp_service_yaml(self, auth_client):
        """Test POST /api/mcp-services/import - YAML形式でインポート"""
        yaml_data = """
name: Imported Service
identifier: imported-service
description: Imported from YAML
apps:
  - name: Imported App
    description: App from import
    service_type: api
    mcp_url: https://api.imported.com
    common_headers:
      Authorization: Bearer IMPORT_TOKEN
    capabilities:
      - name: Imported Capability
        capability_type: resource
        description: Capability from import
        url: https://api.imported.com/resource
        headers:
          Accept: application/json
        body_params: {}
        template_content: null
"""
        
        response = auth_client.post(
            '/api/mcp-services/import',
            data=yaml_data,
            content_type='application/x-yaml'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['mcp_service']['name'] == 'Imported Service'
        assert data['mcp_service']['identifier'] == 'imported-service'
        assert data['identifier_changed'] is False
    
    def test_import_mcp_service_identifier_collision(self, auth_client, db):
        """Test importing with duplicate identifier generates new identifier"""
        # Create existing service
        existing = McpService(
            name='Existing',
            identifier='duplicate-id',
            routing_type='subdomain'
        )
        db.session.add(existing)
        db.session.commit()
        
        # Import with same identifier
        yaml_data = """
name: New Service
identifier: duplicate-id
description: Should get new identifier
apps: []
"""
        
        response = auth_client.post(
            '/api/mcp-services/import',
            data=yaml_data,
            content_type='application/x-yaml'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['identifier_changed'] is True
        assert data['mcp_service']['identifier'] != 'duplicate-id'
        assert data['mcp_service']['identifier'].startswith('duplicate-id-')
    
    def test_import_invalid_yaml(self, auth_client):
        """Test importing invalid YAML returns error"""
        invalid_yaml = """
name: Invalid
identifier: invalid
  this is not valid yaml:
    - malformed
"""
        
        response = auth_client.post(
            '/api/mcp-services/import',
            data=invalid_yaml,
            content_type='application/x-yaml'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'YAML' in data['error']
    
    def test_import_missing_required_fields(self, auth_client):
        """Test importing without required fields returns error"""
        yaml_data = """
description: Missing name and identifier
apps: []
"""
        
        response = auth_client.post(
            '/api/mcp-services/import',
            data=yaml_data,
            content_type='application/x-yaml'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestMcpServiceAppsAPI:
    """Test MCP Service Apps API endpoints"""
    
    def test_get_mcp_service_apps(self, auth_client, db):
        """Test GET /api/mcp-services/<id>/apps"""
        mcp_service = McpService(
            name='Service',
            identifier='service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create apps
        app1 = Service(
            name='App 1',
            service_type='api',
            common_headers='{}',
            mcp_service_id=mcp_service.id
        )
        db.session.add(app1)
        db.session.commit()
        
        response = auth_client.get(f'/api/mcp-services/{mcp_service.id}/apps')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert any(app['name'] == 'App 1' for app in data)
    
    def test_create_app_for_mcp_service(self, auth_client, db):
        """Test POST /api/mcp-services/<id>/apps"""
        mcp_service = McpService(
            name='Service',
            identifier='service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        payload = {
            'name': 'New App',
            'service_type': 'api',
            'common_headers': '{}'
        }
        response = auth_client.post(f'/api/mcp-services/{mcp_service.id}/apps',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'New App'
        assert data['mcp_service_id'] == mcp_service.id


class TestMcpServiceRouting:
    """Test MCP Service routing"""
    
    def test_subdomain_routing(self, db):
        """Test subdomain routing type"""
        mcp_service = McpService(
            name='Subdomain Service',
            identifier='sub-service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        assert mcp_service.routing_type == 'subdomain'
        
        # Endpoint should be: sub-service.domain.com/mcp
    
    def test_path_routing(self, db):
        """Test path routing type"""
        mcp_service = McpService(
            name='Path Service',
            identifier='path-service',
            routing_type='path'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        assert mcp_service.routing_type == 'path'
        
        # Endpoint should be: domain.com/path-service/mcp


class TestMcpServiceAccessControl:
    """Test MCP Service access control"""
    
    def test_public_access(self, db):
        """Test public access control"""
        mcp_service = McpService(
            name='Public Service',
            identifier='public',
            routing_type='subdomain',
            access_control='public'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Public services can be accessed without authentication
        assert mcp_service.access_control == 'public'
    
    def test_restricted_access(self, db):
        """Test restricted access control"""
        mcp_service = McpService(
            name='Restricted Service',
            identifier='restricted',
            routing_type='subdomain',
            access_control='restricted'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Restricted services require authentication
        assert mcp_service.access_control == 'restricted'


class TestMcpServiceViews:
    """Test MCP Service view endpoints"""
    
    def test_mcp_service_list_view(self, auth_client):
        """Test GET /mcp-services"""
        response = auth_client.get('/mcp-services')
        
        assert response.status_code == 200
        assert b'MCP' in response.data or b'mcp' in response.data
    
    def test_mcp_service_new_view(self, auth_client):
        """Test GET /mcp-services/new"""
        response = auth_client.get('/mcp-services/new')
        
        assert response.status_code == 200
    
    def test_mcp_service_detail_view(self, auth_client, db):
        """Test GET /mcp-services/<id>"""
        mcp_service = McpService(
            name='View Service',
            identifier='view-service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        response = auth_client.get(f'/mcp-services/{mcp_service.id}')
        
        assert response.status_code == 200
    
    def test_mcp_service_edit_view(self, auth_client, db):
        """Test GET /mcp-services/<id>/edit"""
        mcp_service = McpService(
            name='Edit Service',
            identifier='edit-service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        response = auth_client.get(f'/mcp-services/{mcp_service.id}/edit')
        
        assert response.status_code == 200
    
    def test_mcp_service_apps_view(self, auth_client, db):
        """Test GET /mcp-services/<id>/apps"""
        mcp_service = McpService(
            name='Apps Service',
            identifier='apps-service',
            routing_type='subdomain'
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        response = auth_client.get(f'/mcp-services/{mcp_service.id}/apps')
        
        assert response.status_code == 200
