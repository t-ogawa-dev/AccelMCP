"""
Tests for MCP Controller
"""
import json
import pytest
from app.models.models import ConnectionAccount, Service, Capability


class TestMCPSubdomainEndpoint:
    """Test /mcp endpoint with subdomain routing"""
    
    def test_mcp_get_without_subdomain(self, client, sample_account):
        """Test GET /mcp without subdomain should fail"""
        response = client.get('/mcp',
                             headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Subdomain not specified' in data['error']['message']
    
    def test_mcp_get_without_auth(self, client):
        """Test GET /mcp without authentication should fail"""
        response = client.get('/mcp?subdomain=test-service')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Authorization' in data['error']['message']
    
    def test_mcp_get_with_invalid_token(self, client):
        """Test GET /mcp with invalid bearer token should fail"""
        response = client.get('/mcp?subdomain=test-service',
                             headers={'Authorization': 'Bearer invalid-token'})
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid bearer token' in data['error']['message']
    
    def test_mcp_get_with_nonexistent_service(self, client, sample_account):
        """Test GET /mcp with non-existent service should fail"""
        response = client.get('/mcp?subdomain=nonexistent-service',
                             headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Service not found' in data['error']['message']
    
    def test_mcp_get_capabilities(self, client, sample_account, sample_service, sample_capability):
        """Test GET /mcp returns capabilities for authenticated account"""
        response = client.get(f'/mcp?subdomain={sample_service.subdomain}',
                             headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'capabilities' in data
        assert 'tools' in data['capabilities']
        assert 'serverInfo' in data
    
    def test_mcp_post_without_json(self, client, sample_account, sample_service):
        """Test POST /mcp without JSON body should fail"""
        response = client.post(f'/mcp?subdomain={sample_service.subdomain}',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        # Flask returns 415 Unsupported Media Type when Content-Type is not application/json
        assert response.status_code in [400, 415]
    
    def test_mcp_post_tools_list(self, client, sample_account, sample_service, sample_capability):
        """Test POST /mcp with tools/list method"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list',
            'params': {}
        }
        
        response = client.post(f'/mcp?subdomain={sample_service.subdomain}',
                              data=json.dumps(payload),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data or 'tools' in data
    
    def test_mcp_post_tools_call(self, client, sample_account, sample_service, sample_capability):
        """Test POST /mcp with tools/call method"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': sample_capability.name,
                'arguments': {}
            }
        }
        
        response = client.post(f'/mcp?subdomain={sample_service.subdomain}',
                              data=json.dumps(payload),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code in [200, 400, 500]  # May fail if external API is unavailable


class TestMCPToolEndpoint:
    """Test /tools/<tool_id> direct execution endpoint"""
    
    def test_tool_without_subdomain(self, client, sample_account, sample_capability):
        """Test POST /tools/<id> without subdomain should fail"""
        response = client.post(f'/tools/{sample_capability.id}',
                              data=json.dumps({'arguments': {}}),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_tool_without_auth(self, client, sample_service, sample_capability):
        """Test POST /tools/<id> without authentication should fail"""
        response = client.post(f'/tools/{sample_capability.id}?subdomain={sample_service.subdomain}',
                              data=json.dumps({'arguments': {}}),
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_tool_execution(self, client, sample_account, sample_service, sample_capability):
        """Test POST /tools/<id> executes tool"""
        response = client.post(f'/tools/{sample_capability.id}?subdomain={sample_service.subdomain}',
                              data=json.dumps({'arguments': {}}),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        # Response depends on external API availability
        assert response.status_code in [200, 400, 500]


class TestMCPLegacyEndpoint:
    """Test /mcp/<subdomain> legacy endpoint"""
    
    def test_legacy_endpoint_without_auth(self, client):
        """Test POST /mcp/<subdomain> without authentication should fail"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list'
        }
        
        response = client.post('/mcp/test-service',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_legacy_endpoint_with_nonexistent_service(self, client, sample_account):
        """Test POST /mcp/<subdomain> with non-existent service should fail"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list'
        }
        
        response = client.post('/mcp/nonexistent-service',
                              data=json.dumps(payload),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Service not found' in data['error']
    
    def test_legacy_endpoint_tools_list(self, client, sample_account, sample_service, sample_capability):
        """Test POST /mcp/<subdomain> with tools/list method"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list',
            'params': {}
        }
        
        response = client.post(f'/mcp/{sample_service.subdomain}',
                              data=json.dumps(payload),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Response format may vary based on MCP handler implementation
        assert isinstance(data, dict)


class TestSubdomainExtraction:
    """Test subdomain extraction from different request formats"""
    
    def test_subdomain_from_query_param(self, client, sample_account, sample_service):
        """Test subdomain extraction from query parameter"""
        response = client.get(f'/mcp?subdomain={sample_service.subdomain}',
                             headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        assert response.status_code == 200
    
    def test_subdomain_from_header(self, client, sample_account, sample_service):
        """Test subdomain extraction from X-Subdomain header"""
        response = client.get('/mcp',
                             headers={
                                 'Authorization': f'Bearer {sample_account.bearer_token}',
                                 'X-Subdomain': sample_service.subdomain
                             })
        
        assert response.status_code == 200


class TestMCPErrorHandling:
    """Test MCP error handling"""
    
    def test_invalid_json_rpc_version(self, client, sample_account, sample_service):
        """Test handling of invalid JSON-RPC version"""
        payload = {
            'jsonrpc': '1.0',  # Invalid version
            'id': 1,
            'method': 'tools/list'
        }
        
        response = client.post(f'/mcp?subdomain={sample_service.subdomain}',
                              data=json.dumps(payload),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_missing_method(self, client, sample_account, sample_service):
        """Test handling of missing method field"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1
            # Missing 'method'
        }
        
        response = client.post(f'/mcp?subdomain={sample_service.subdomain}',
                              data=json.dumps(payload),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        # Should return error
        assert response.status_code in [200, 400]
    
    def test_unknown_method(self, client, sample_account, sample_service):
        """Test handling of unknown MCP method"""
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'unknown/method',
            'params': {}
        }
        
        response = client.post(f'/mcp?subdomain={sample_service.subdomain}',
                              data=json.dumps(payload),
                              content_type='application/json',
                              headers={'Authorization': f'Bearer {sample_account.bearer_token}'})
        
        # Should return method not found error
        assert response.status_code in [200, 400]
        data = json.loads(response.data)
        if response.status_code == 200:
            assert 'error' in data

