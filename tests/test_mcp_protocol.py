"""
Tests for MCP Protocol endpoints
Tests tools/list, resources/list, resources/read, prompts/list, prompts/get
"""
import json
import pytest
from app.models.models import McpService, Service, Capability, ConnectionAccount, Resource


class TestMcpProtocolToolsList:
    """Test tools/list endpoint"""
    
    def test_tools_list_public_access(self, client, db):
        """Test tools/list with public MCP service"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP',
            identifier='public-mcp',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create an app under this MCP service
        app = Service(
            name='Test App',
            service_type='api',
            mcp_url='https://api.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create capabilities
        cap1 = Capability(
            name='get_weather',
            description='Get weather information',
            capability_type='tool',
            app_id=app.id,
            url='/weather',
            headers='{}',
            body_params='{"properties": {"city": {"type": "string", "description": "City name"}}, "required": []}',
            is_enabled=True,
            access_control='public'
        )
        cap2 = Capability(
            name='get_forecast',
            description='Get weather forecast',
            capability_type='tool',
            app_id=app.id,
            url='/forecast',
            headers='{}',
            body_params='{}',
            is_enabled=True,
            access_control='public'
        )
        db.session.add_all([cap1, cap2])
        db.session.commit()
        
        # Send tools/list request
        response = client.post(
            '/mcp?subdomain=public-mcp',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'jsonrpc' in data
        assert data['jsonrpc'] == '2.0'
        assert 'result' in data
        assert 'tools' in data['result']
        
        tools = data['result']['tools']
        assert len(tools) == 2
        
        # Check tool structure
        for tool in tools:
            assert 'name' in tool
            assert 'description' in tool
            assert 'inputSchema' in tool
    
    def test_tools_list_restricted_access_with_auth(self, client, db):
        """Test tools/list with restricted MCP service and authentication"""
        # Create restricted MCP service
        mcp_service = McpService(
            name='Restricted MCP',
            identifier='restricted-mcp',
            routing_type='subdomain',
            access_control='restricted',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create connection account
        account = ConnectionAccount(
            name='Test Account',
            bearer_token='test-token-123'
        )
        db.session.add(account)
        db.session.commit()
        
        # Grant permission to account
        from app.models.models import AccountPermission
        permission = AccountPermission(
            account_id=account.id,
            mcp_service_id=mcp_service.id
        )
        db.session.add(permission)
        db.session.commit()
        
        # Create app and capability
        app = Service(
            name='Secure App',
            service_type='api',
            mcp_url='https://api.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        cap = Capability(
            name='secure_tool',
            description='Secure tool',
            capability_type='tool',
            app_id=app.id,
            url='/secure',
            headers='{}',
            body_params='{}',
            is_enabled=True,
            access_control='public'
        )
        db.session.add(cap)
        db.session.commit()
        
        # Send tools/list request with authentication
        response = client.post(
            '/mcp?subdomain=restricted-mcp',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/list',
                'params': {}
            }),
            headers={'Authorization': 'Bearer test-token-123'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'tools' in data['result']
        assert len(data['result']['tools']) >= 1
    
    def test_tools_list_restricted_access_without_auth(self, client, db):
        """Test tools/list with restricted MCP service without authentication"""
        # Create restricted MCP service
        mcp_service = McpService(
            name='Restricted MCP 2',
            identifier='restricted-mcp-2',
            routing_type='subdomain',
            access_control='restricted',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send tools/list request without authentication
        response = client.post(
            '/mcp?subdomain=restricted-mcp-2',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data


class TestMcpProtocolToolsCall:
    """Test tools/call endpoint"""
    
    def test_tools_call_success(self, client, db):
        """Test tools/call with valid tool"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Call',
            identifier='public-mcp-call',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create app
        app = Service(
            name='Test App',
            service_type='api',
            mcp_url='https://api.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create tool capability
        tool = Capability(
            name='test_tool',
            description='Test tool',
            capability_type='tool',
            app_id=app.id,
            url='https://httpbin.org/post',
            headers='{}',
            body_params='{"properties": {"input": {"type": "string"}}, "required": []}',
            is_enabled=True,
            access_control='public'
        )
        db.session.add(tool)
        db.session.commit()
        
        # Send tools/call request with new format: {mcp_identifier}_{app_name}:{capability_name}
        response = client.post(
            '/mcp?subdomain=public-mcp-call',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/call',
                'params': {
                    'name': 'public-mcp-call_Test_App:test_tool',
                    'arguments': {
                        'input': 'test value'
                    }
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have result with content
        assert 'result' in data or 'error' in data
    
    def test_tools_call_tool_not_found(self, client, db):
        """Test tools/call with non-existent tool"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Call 2',
            identifier='public-mcp-call2',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send tools/call request for non-existent tool
        response = client.post(
            '/mcp?subdomain=public-mcp-call2',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/call',
                'params': {
                    'name': 'nonexistent_tool',
                    'arguments': {}
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return error
        assert 'error' in data
    
    def test_tools_call_missing_params(self, client, db):
        """Test tools/call without required params"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Call 3',
            identifier='public-mcp-call3',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send tools/call request without name
        response = client.post(
            '/mcp?subdomain=public-mcp-call3',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/call',
                'params': {
                    'arguments': {}
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return error
        assert 'error' in data

    def test_tools_call_with_tool_type_capability(self, client, db):
        """Test tools/call with capability_type='tool' (not 'api')"""
        # Create public MCP service
        mcp_service = McpService(
            name='Tool Type Test',
            identifier='tool-type-test',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create app
        app = Service(
            name='Weather App',
            service_type='api',
            mcp_url='https://weather.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create tool with 'tool' type
        tool = Capability(
            name='get_weather',
            description='Get weather forecast',
            capability_type='tool',  # Testing 'tool' type specifically
            app_id=app.id,
            url='https://httpbin.org/post',
            headers='{}',
            body_params='{"properties": {"city": {"type": "string"}}, "required": ["city"]}',
            is_enabled=True,
            access_control='public'
        )
        db.session.add(tool)
        db.session.commit()
        
        # Send tools/call request with new format
        response = client.post(
            '/mcp?subdomain=tool-type-test',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/call',
                'params': {
                    'name': 'tool-type-test_Weather_App:get_weather',
                    'arguments': {
                        'city': '130000'
                    }
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should not return 'Unknown capability type: tool' error
        assert 'result' in data
        assert 'content' in data['result']

    def test_tools_list_with_empty_app_name(self, client, db):
        """Test tools/list when app name is empty or special characters"""
        # Create public MCP service
        mcp_service = McpService(
            name='Empty Name Test',
            identifier='empty-name-test',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create app with special characters only
        app = Service(
            name=':::',  # Special characters that become underscores
            service_type='api',
            mcp_url='https://api.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create tool
        tool = Capability(
            name='test_tool',
            description='Test tool',
            capability_type='tool',
            app_id=app.id,
            url='https://httpbin.org/post',
            headers='{}',
            body_params='{}',
            is_enabled=True,
            access_control='public'
        )
        db.session.add(tool)
        db.session.commit()
        
        # Send tools/list request
        response = client.post(
            '/mcp?subdomain=empty-name-test',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'tools' in data['result']
        assert len(data['result']['tools']) == 1
        
        tool_name = data['result']['tools'][0]['name']
        # Should use 'app' as fallback, not '____'
        assert not tool_name.startswith('____:')
        assert not tool_name.startswith('_:::')
        # Should start with 'app:' or a valid name
        assert ':' in tool_name
        
        # Now test tools/call with the same namespaced tool name
        response = client.post(
            '/mcp?subdomain=empty-name-test',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 2,
                'method': 'tools/call',
                'params': {
                    'name': tool_name,  # Use the exact name from tools/list
                    'arguments': {}
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should successfully find and execute the tool (not 'Tool not found' error)
        assert 'result' in data
        assert 'content' in data['result']


class TestMcpProtocolResourcesList:
    """Test resources/list endpoint"""
    
    def test_resources_list_empty(self, client, db):
        """Test resources/list with no resources"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP',
            identifier='public-mcp-res',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send resources/list request
        response = client.post(
            '/mcp?subdomain=public-mcp-res',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'resources/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'jsonrpc' in data
        assert data['jsonrpc'] == '2.0'
        assert 'result' in data
        assert 'resources' in data['result']
        assert isinstance(data['result']['resources'], list)
    
    def test_resources_list_with_global_resources(self, client, db):
        """Test resources/list with global resources"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Res',
            identifier='public-mcp-res2',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create service/app under this MCP service
        app = Service(
            name='Resource Test App',
            mcp_service_id=mcp_service.id,
            service_type='mcp_builtin',
            description='Test app with resources',
            is_enabled=True
        )
        db.session.add(app)
        db.session.commit()
        
        # Create global resources in Resource table
        resource1 = Resource(
            resource_id=Resource.generate_resource_id(),
            name='test_document',
            description='Test document resource',
            content='This is a test document',
            mime_type='text/plain',
            access_control='public',
            is_enabled=True
        )
        resource2 = Resource(
            resource_id=Resource.generate_resource_id(),
            name='api_spec',
            description='API specification',
            content='{"version": "1.0"}',
            mime_type='application/json',
            access_control='public',
            is_enabled=True
        )
        db.session.add_all([resource1, resource2])
        db.session.commit()
        
        # Create resource-type capabilities that reference global resources
        cap1 = Capability(
            app_id=app.id,
            name='test_document',
            capability_type='resource',
            global_resource_id=resource1.id,
            description='Test document resource',
            resource_mime_type='text/plain',
            access_control='public',
            is_enabled=True
        )
        cap2 = Capability(
            app_id=app.id,
            name='api_spec',
            capability_type='resource',
            global_resource_id=resource2.id,
            description='API specification',
            resource_mime_type='application/json',
            access_control='public',
            is_enabled=True
        )
        db.session.add_all([cap1, cap2])
        db.session.commit()
        
        # Send resources/list request
        response = client.post(
            '/mcp?subdomain=public-mcp-res2',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'resources/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'resources' in data['result']
        
        resources = data['result']['resources']
        assert len(resources) >= 2
        
        # Check resource structure
        for resource in resources:
            assert 'uri' in resource
            assert 'name' in resource
            assert 'description' in resource
            assert 'mimeType' in resource
    
    def test_resources_list_with_capability_resources(self, client, db):
        """Test resources/list with resource-type capabilities"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Res3',
            identifier='public-mcp-res3',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create app
        app = Service(
            name='Resource App',
            service_type='api',
            mcp_url='https://api.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create resource-type capability
        resource_cap = Capability(
            name='docs',
            description='Documentation resource',
            capability_type='resource',
            app_id=app.id,
            url='/docs',
            headers='{}',
            resource_uri='resource://res-app/docs',
            resource_mime_type='text/plain',
            is_enabled=True,
            access_control='public'
        )
        db.session.add(resource_cap)
        db.session.commit()
        
        # Send resources/list request
        response = client.post(
            '/mcp?subdomain=public-mcp-res3',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'resources/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'resources' in data['result']
        
        resources = data['result']['resources']
        assert len(resources) >= 1


class TestMcpProtocolResourcesRead:
    """Test resources/read endpoint"""
    
    def test_resources_read_global_resource(self, client, db):
        """Test resources/read for global resource"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Read',
            identifier='public-mcp-read',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create service/app under this MCP service
        app = Service(
            name='Resource Read Test App',
            mcp_service_id=mcp_service.id,
            service_type='mcp_builtin',
            description='Test app for resource read',
            is_enabled=True
        )
        db.session.add(app)
        db.session.commit()
        
        # Create global resource
        resource = Resource(
            resource_id=Resource.generate_resource_id(),
            name='test_doc',
            description='Test document',
            content='Hello, World!',
            mime_type='text/plain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(resource)
        db.session.commit()
        
        # Create resource-type capability that references the global resource
        resource_uri = f'resource://public-mcp-read/test_doc'
        cap = Capability(
            app_id=app.id,
            name='test_doc',
            capability_type='resource',
            global_resource_id=resource.id,
            resource_uri=resource_uri,
            template_content=resource.content,  # Copy content for resources/read
            description='Test document',
            resource_mime_type='text/plain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(cap)
        db.session.commit()
        
        # Send resources/read request
        response = client.post(
            '/mcp?subdomain=public-mcp-read',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'resources/read',
                'params': {
                    'uri': resource_uri
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'contents' in data['result']
        assert len(data['result']['contents']) == 1
        
        content = data['result']['contents'][0]
        assert content['uri'] == resource_uri  # Check capability resource_uri, not global resource URI
        assert content['mimeType'] == 'text/plain'
        assert content['text'] == 'Hello, World!'
    
    def test_resources_read_missing_uri(self, client, db):
        """Test resources/read without uri parameter"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Read 2',
            identifier='public-mcp-read2',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send resources/read request without uri
        response = client.post(
            '/mcp?subdomain=public-mcp-read2',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'resources/read',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == -32602
        assert 'uri' in data['error']['message'].lower()


class TestMcpProtocolPromptsList:
    """Test prompts/list endpoint"""
    
    def test_prompts_list_empty(self, client, db):
        """Test prompts/list with no prompts"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Prompts',
            identifier='public-mcp-prompts',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send prompts/list request
        response = client.post(
            '/mcp?subdomain=public-mcp-prompts',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'prompts/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'jsonrpc' in data
        assert data['jsonrpc'] == '2.0'
        assert 'result' in data
        assert 'prompts' in data['result']
        assert isinstance(data['result']['prompts'], list)
    
    def test_prompts_list_with_prompts(self, client, db):
        """Test prompts/list with prompt capabilities"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Prompts 2',
            identifier='public-mcp-prompts2',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create app
        app = Service(
            name='Prompt App',
            service_type='api',
            mcp_url='https://api.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create prompt capabilities
        prompt1 = Capability(
            name='greeting_prompt',
            description='Generate a greeting',
            capability_type='prompt',
            app_id=app.id,
            url='',
            headers='{}',
            template_content='Hello {{name}}!',
            body_params='{"properties": {"name": {"type": "string", "description": "Name to greet"}}, "required": ["name"]}',
            is_enabled=True,
            access_control='public'
        )
        prompt2 = Capability(
            name='farewell_prompt',
            description='Generate a farewell',
            capability_type='prompt',
            app_id=app.id,
            url='',
            headers='{}',
            template_content='Goodbye {{name}}!',
            body_params='{"properties": {"name": {"type": "string", "description": "Name"}}, "required": []}',
            is_enabled=True,
            access_control='public'
        )
        db.session.add_all([prompt1, prompt2])
        db.session.commit()
        
        # Send prompts/list request
        response = client.post(
            '/mcp?subdomain=public-mcp-prompts2',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'prompts/list',
                'params': {}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'prompts' in data['result']
        
        prompts = data['result']['prompts']
        assert len(prompts) == 2
        
        # Check prompt structure
        for prompt in prompts:
            assert 'name' in prompt
            assert 'description' in prompt
        
        # Check for arguments
        greeting_prompt = next(p for p in prompts if p['name'] == 'greeting_prompt')
        assert 'arguments' in greeting_prompt
        assert len(greeting_prompt['arguments']) >= 1


class TestMcpProtocolPromptsGet:
    """Test prompts/get endpoint"""
    
    def test_prompts_get_success(self, client, db):
        """Test prompts/get with valid prompt"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Get',
            identifier='public-mcp-get',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create app
        app = Service(
            name='Prompt App',
            service_type='api',
            mcp_url='https://api.example.com',
            mcp_service_id=mcp_service.id,
            is_enabled=True,
            access_control='public'
        )
        db.session.add(app)
        db.session.commit()
        
        # Create prompt capability
        prompt = Capability(
            name='test_prompt',
            description='Test prompt template',
            capability_type='prompt',
            app_id=app.id,
            url='',
            headers='{}',
            template_content='Hello {{name}}, you are {{age}} years old.',
            body_params='{"properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": []}',
            is_enabled=True,
            access_control='public'
        )
        db.session.add(prompt)
        db.session.commit()
        
        # Send prompts/get request
        response = client.post(
            '/mcp?subdomain=public-mcp-get',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'prompts/get',
                'params': {
                    'name': 'test_prompt',
                    'arguments': {
                        'name': 'Alice',
                        'age': '30'
                    }
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'description' in data['result']
        assert 'messages' in data['result']
        assert len(data['result']['messages']) == 1
        
        message = data['result']['messages'][0]
        assert message['role'] == 'user'
        assert message['content']['type'] == 'text'
        assert 'Alice' in message['content']['text']
        assert '30' in message['content']['text']
    
    def test_prompts_get_not_found(self, client, db):
        """Test prompts/get with non-existent prompt"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Get 2',
            identifier='public-mcp-get2',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send prompts/get request for non-existent prompt
        response = client.post(
            '/mcp?subdomain=public-mcp-get2',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'prompts/get',
                'params': {
                    'name': 'nonexistent_prompt',
                    'arguments': {}
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'error' in data
        assert 'not found' in data['error']['message'].lower()
    
    def test_prompts_get_missing_name(self, client, db):
        """Test prompts/get without name parameter"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Get 3',
            identifier='public-mcp-get3',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Send prompts/get request without name
        response = client.post(
            '/mcp?subdomain=public-mcp-get3',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'prompts/get',
                'params': {
                    'arguments': {}
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'error' in data
        assert data['error']['code'] == -32602


class TestMcpProtocolInitialize:
    """Test initialize endpoint"""
    
    def test_initialize_request(self, client, db):
        """Test initialize request"""
        # Create public MCP service
        mcp_service = McpService(
            name='Public MCP Init',
            identifier='public-mcp-init',
            routing_type='subdomain',
            access_control='public',
            is_enabled=True
        )
        db.session.add(mcp_service)
        db.session.commit()
        
        # Create service/app under this MCP service
        app = Service(
            name='Init Test App',
            mcp_service_id=mcp_service.id,
            service_type='api',
            description='Test app for initialize',
            is_enabled=True
        )
        db.session.add(app)
        db.session.commit()
        
        # Create capabilities of different types to populate capabilities
        tool_cap = Capability(
            app_id=app.id,
            name='test_tool',
            capability_type='tool',
            url='https://api.example.com/test',
            description='Test tool capability',
            access_control='public',
            is_enabled=True
        )
        resource_cap = Capability(
            app_id=app.id,
            name='test_resource',
            capability_type='resource',
            description='Test resource capability',
            template_content='Test content',
            resource_mime_type='text/plain',
            access_control='public',
            is_enabled=True
        )
        prompt_cap = Capability(
            app_id=app.id,
            name='test_prompt',
            capability_type='prompt',
            description='Test prompt capability',
            template_content='Test prompt template',
            access_control='public',
            is_enabled=True
        )
        db.session.add_all([tool_cap, resource_cap, prompt_cap])
        db.session.commit()
        
        # Send initialize request
        response = client.post(
            '/mcp?subdomain=public-mcp-init',
            data=json.dumps({
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'initialize',
                'params': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {},
                    'clientInfo': {
                        'name': 'test-client',
                        'version': '1.0.0'
                    }
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'result' in data
        assert 'protocolVersion' in data['result']
        assert 'capabilities' in data['result']
        assert 'serverInfo' in data['result']
        assert 'sessionId' in data['result']
        
        # Check capabilities structure
        capabilities = data['result']['capabilities']
        assert 'tools' in capabilities
        assert 'resources' in capabilities
        assert 'prompts' in capabilities
