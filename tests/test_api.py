"""
Tests for API controllers
"""
import json
import pytest


class TestServiceAPI:
    """Test Service API endpoints"""
    
    def test_get_services(self, auth_client, sample_service):
        """Test GET /api/services"""
        response = auth_client.get('/api/services')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert data[0]['subdomain'] == 'test-service'
    
    def test_create_service(self, auth_client):
        """Test POST /api/services"""
        payload = {
            'subdomain': 'new-service',
            'name': 'New Service',
            'service_type': 'api',
            'description': 'New service description',
            'common_headers': '{}'
        }
        response = auth_client.post('/api/services',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['subdomain'] == 'new-service'
        assert data['name'] == 'New Service'
    
    def test_get_service_detail(self, auth_client, sample_service):
        """Test GET /api/services/<id>"""
        response = auth_client.get(f'/api/services/{sample_service.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_service.id
        assert data['subdomain'] == 'test-service'
    
    def test_update_service(self, auth_client, sample_service):
        """Test PUT /api/services/<id>"""
        payload = {
            'name': 'Updated Service',
            'description': 'Updated description'
        }
        response = auth_client.put(f'/api/services/{sample_service.id}',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated Service'
    
    def test_delete_service(self, auth_client, sample_service):
        """Test DELETE /api/services/<id>"""
        service_id = sample_service.id
        response = auth_client.delete(f'/api/services/{service_id}')
        
        assert response.status_code == 204
        
        # Verify deletion
        response = auth_client.get(f'/api/services/{service_id}')
        assert response.status_code == 404


class TestCapabilityAPI:
    """Test Capability API endpoints"""
    
    def test_get_capabilities(self, auth_client, sample_capability):
        """Test GET /api/services/<service_id>/capabilities"""
        service_id = sample_capability.service_id
        response = auth_client.get(f'/api/services/{service_id}/capabilities')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
    
    def test_create_capability(self, auth_client, sample_service):
        """Test POST /api/services/<service_id>/capabilities"""
        payload = {
            'name': 'new_capability',
            'capability_type': 'tool',
            'url': 'https://api.example.com/new',
            'headers': '{}',
            'body_params': '{}',
            'description': 'New capability'
        }
        response = auth_client.post(f'/api/services/{sample_service.id}/capabilities',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'new_capability'
    
    def test_get_capability_detail(self, auth_client, sample_capability):
        """Test GET /api/capabilities/<id>"""
        response = auth_client.get(f'/api/capabilities/{sample_capability.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_capability.id
    
    def test_update_capability(self, auth_client, sample_capability):
        """Test PUT /api/capabilities/<id>"""
        payload = {
            'name': 'updated_capability',
            'description': 'Updated description'
        }
        response = auth_client.put(f'/api/capabilities/{sample_capability.id}',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'updated_capability'
    
    def test_toggle_capability(self, auth_client, sample_capability):
        """Test POST /api/capabilities/<id>/toggle"""
        original_state = sample_capability.is_enabled
        response = auth_client.post(f'/api/capabilities/{sample_capability.id}/toggle')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['is_enabled'] != original_state
    
    def test_delete_capability(self, auth_client, sample_capability):
        """Test DELETE /api/capabilities/<id>"""
        capability_id = sample_capability.id
        response = auth_client.delete(f'/api/capabilities/{capability_id}')
        
        assert response.status_code == 204
        
        # Verify deletion
        response = auth_client.get(f'/api/capabilities/{capability_id}')
        assert response.status_code == 404


class TestConnectionAccountAPI:
    """Test ConnectionAccount API endpoints"""
    
    def test_get_accounts(self, auth_client, sample_account):
        """Test GET /api/accounts"""
        response = auth_client.get('/api/accounts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
    
    def test_create_account(self, auth_client):
        """Test POST /api/accounts"""
        payload = {
            'name': 'New Account',
            'description': 'New account description'
        }
        response = auth_client.post('/api/accounts',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'New Account'
        assert 'bearer_token' in data
    
    def test_get_account_detail(self, auth_client, sample_account):
        """Test GET /api/accounts/<id>"""
        response = auth_client.get(f'/api/accounts/{sample_account.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_account.id
    
    def test_update_account(self, auth_client, sample_account):
        """Test PUT /api/accounts/<id>"""
        payload = {
            'name': 'Updated Account',
            'description': 'Updated description'
        }
        response = auth_client.put(f'/api/accounts/{sample_account.id}',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated Account'
    
    def test_delete_account(self, auth_client, sample_account):
        """Test DELETE /api/accounts/<id>"""
        account_id = sample_account.id
        response = auth_client.delete(f'/api/accounts/{account_id}')
        
        assert response.status_code == 204


class TestTemplateAPI:
    """Test Template API endpoints"""
    
    def test_get_templates(self, auth_client, sample_template):
        """Test GET /api/templates"""
        response = auth_client.get('/api/mcp-templates')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
    
    def test_create_template(self, auth_client):
        """Test POST /api/templates"""
        payload = {
            'name': 'New Template',
            'template_type': 'custom',
            'service_type': 'api',
            'description': 'New template',
            'common_headers': '{}',
            'icon': '🆕',
            'category': 'Custom'
        }
        response = auth_client.post('/api/mcp-templates',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'New Template'
    
    def test_get_template_detail(self, auth_client, sample_template):
        """Test GET /api/templates/<id>"""
        response = auth_client.get(f'/api/mcp-templates/{sample_template.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_template.id
    
    def test_update_template(self, auth_client, sample_template):
        """Test PUT /api/templates/<id>"""
        payload = {
            'name': 'Updated Template',
            'description': 'Updated description'
        }
        response = auth_client.put(f'/api/mcp-templates/{sample_template.id}',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated Template'
    
    def test_delete_template(self, auth_client, sample_template):
        """Test DELETE /api/templates/<id>"""
        template_id = sample_template.id
        response = auth_client.delete(f'/api/mcp-templates/{template_id}')
        
        assert response.status_code == 204
    
    def test_export_template(self, auth_client, sample_template):
        """Test GET /api/templates/<id>/export"""
        response = auth_client.get(f'/api/mcp-templates/{sample_template.id}/export')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_import_template(self, auth_client, sample_template):
        """Test POST /api/templates/import"""
        # First export
        export_response = auth_client.get(f'/api/mcp-templates/{sample_template.id}/export')
        template_data = json.loads(export_response.data)
        
        # Modify name to avoid conflict
        template_data['name'] = 'Imported Template'
        
        # Import
        response = auth_client.post('/api/mcp-templates/import',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Imported Template'


class TestMcpCapabilityTemplateAPI:
    """Test Capability Template API endpoints"""
    
    def test_get_capability_templates(self, auth_client, sample_capability_template):
        """Test GET /api/templates/<template_id>/capabilities"""
        template_id = sample_capability_template.service_template_id
        response = auth_client.get(f'/api/mcp-templates/{template_id}/capabilities')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
    
    def test_create_capability_template(self, auth_client, sample_template):
        """Test POST /api/templates/<template_id>/capabilities"""
        payload = {
            'name': 'new_template_cap',
            'capability_type': 'tool',
            'url': 'https://api.example.com/template',
            'headers': '{}',
            'body_params': '{}',
            'description': 'New template capability'
        }
        response = auth_client.post(f'/api/mcp-templates/{sample_template.id}/capabilities',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'new_template_cap'
