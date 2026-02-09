"""
Test for Prompt and Resource Capability functionality
Tests for today's changes including:
- Prompt capability creation without creating Resource records
- Resource capability creation with Resource records
- prompts/get endpoint with template_content and Resource table fallback
- Capability list API response handling for different types
"""
import pytest
import json
from app.models.models import Capability, Resource, Service, McpService


@pytest.fixture
def sample_mcp_service_for_prompt(db):
    """Create sample MCP service for prompt testing"""
    mcp_service = McpService(
        identifier='test-prompt-mcp',
        name='Test Prompt MCP',
        routing_type='path',  # Use path-based routing for testing
        access_control='public'
    )
    db.session.add(mcp_service)
    db.session.commit()
    return mcp_service


@pytest.fixture
def sample_service_for_prompt(db, sample_mcp_service_for_prompt):
    """Create sample service for prompt testing"""
    service = Service(
        mcp_service_id=sample_mcp_service_for_prompt.id,
        name='Test Prompt Service',
        service_type='mcp_builtin',
        description='Test prompt service',
        common_headers='{}'
    )
    db.session.add(service)
    db.session.commit()
    return service


@pytest.fixture
def sample_global_resource(db):
    """Create sample global resource"""
    resource = Resource(
        name='Test Resource Template',
        resource_id='test://resource/template',
        mime_type='text/plain',
        content='Hello {{name}}, you are {{role}}.',
        description='Test resource template'
    )
    db.session.add(resource)
    db.session.commit()
    return resource


@pytest.fixture
def sample_connection_account(db):
    """Create sample connection account for MCP authentication"""
    from app.models.models import ConnectionAccount
    account = ConnectionAccount(
        name='Test Bearer Account',
        bearer_token='test_bearer_token_for_prompt_tests',
        notes='Test account for prompt capability tests'
    )
    db.session.add(account)
    db.session.commit()
    return account


class TestPromptCapabilityCreation:
    """Test prompt capability creation does not create Resource records"""
    
    def test_create_prompt_capability_without_resource_record(self, auth_client, db, sample_service_for_prompt):
        """Test that creating a prompt capability does NOT create a Resource record"""
        # Initial resource count
        initial_resource_count = Resource.query.count()
        
        # Create prompt capability
        data = {
            'name': 'test_prompt',
            'capability_type': 'prompt',
            'template_content': 'Hello {{name}}, you are a {{role}}.',
            'description': 'Test prompt capability',
            'access_control': 'public'
        }
        
        response = auth_client.post(
            f'/api/apps/{sample_service_for_prompt.id}/capabilities',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = json.loads(response.data)
        
        # Verify capability was created
        capability = Capability.query.filter_by(id=result['id']).first()
        assert capability is not None
        assert capability.capability_type == 'prompt'
        assert capability.template_content == 'Hello {{name}}, you are a {{role}}.'
        assert capability.global_resource_id is None
        
        # Verify NO new Resource record was created
        final_resource_count = Resource.query.count()
        assert final_resource_count == initial_resource_count
    
    def test_create_tool_capability_without_resource_record(self, auth_client, db, sample_service_for_prompt):
        """Test that creating a tool capability does NOT create a Resource record"""
        initial_resource_count = Resource.query.count()
        
        # Create tool capability
        data = {
            'name': 'test_tool',
            'capability_type': 'tool',
            'url': 'https://api.example.com/test',
            'description': 'Test tool capability',
            'access_control': 'public',
            'headers': {},
            'body_params': {}
        }
        
        response = auth_client.post(
            f'/api/apps/{sample_service_for_prompt.id}/capabilities',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = json.loads(response.data)
        
        # Verify capability was created
        capability = Capability.query.filter_by(id=result['id']).first()
        assert capability is not None
        assert capability.capability_type == 'tool'
        assert capability.global_resource_id is None
        
        # Verify NO new Resource record was created
        final_resource_count = Resource.query.count()
        assert final_resource_count == initial_resource_count


class TestResourceCapabilityCreation:
    """Test resource capability creation creates Resource records"""
    
    def test_create_resource_capability_with_new_resource(self, auth_client, db, sample_service_for_prompt):
        """Test that creating a resource capability with new content creates a Resource record"""
        initial_resource_count = Resource.query.count()
        
        # Create resource capability with new resource
        data = {
            'name': 'test_resource',
            'capability_type': 'resource',
            'resource_uri': 'test://new/resource',
            'template_content': 'New resource content',
            'description': 'Test resource capability',
            'access_control': 'public'
        }
        
        response = auth_client.post(
            f'/api/apps/{sample_service_for_prompt.id}/capabilities',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = json.loads(response.data)
        
        # Verify capability was created
        capability = Capability.query.filter_by(id=result['id']).first()
        assert capability is not None
        assert capability.capability_type == 'resource'
        assert capability.global_resource_id is not None
        
        # Verify a new Resource record WAS created
        final_resource_count = Resource.query.count()
        assert final_resource_count == initial_resource_count + 1
        
        # Verify the Resource record content
        resource = db.session.get(Resource, capability.global_resource_id)
        assert resource is not None
        assert resource.content == 'New resource content'
        # Note: resource_id is auto-generated, so we just verify it exists
        assert resource.resource_id is not None
    
    def test_create_resource_capability_with_existing_resource(self, auth_client, db, sample_service_for_prompt, sample_global_resource):
        """Test that creating a resource capability with existing resource does NOT create a new Resource record"""
        initial_resource_count = Resource.query.count()
        
        # Create resource capability using existing resource
        data = {
            'name': 'test_resource_existing',
            'capability_type': 'resource',
            'global_resource_id': sample_global_resource.id,
            'description': 'Test resource capability with existing resource',
            'access_control': 'public'
        }
        
        response = auth_client.post(
            f'/api/apps/{sample_service_for_prompt.id}/capabilities',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        result = json.loads(response.data)
        
        # Verify capability was created
        capability = Capability.query.filter_by(id=result['id']).first()
        assert capability is not None
        assert capability.capability_type == 'resource'
        assert capability.global_resource_id == sample_global_resource.id
        
        # Verify NO new Resource record was created
        final_resource_count = Resource.query.count()
        assert final_resource_count == initial_resource_count


class TestPromptCapabilityUpdate:
    """Test prompt capability update does not create Resource records"""
    
    def test_update_prompt_capability_without_resource_record(self, auth_client, db, sample_service_for_prompt):
        """Test that updating a prompt capability does NOT create a Resource record"""
        # Create initial prompt capability
        prompt_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='initial_prompt',
            capability_type='prompt',
            template_content='Initial template',
            description='Initial prompt',
            is_enabled=True
        )
        db.session.add(prompt_cap)
        db.session.commit()
        
        initial_resource_count = Resource.query.count()
        
        # Update prompt capability
        data = {
            'name': 'updated_prompt',
            'capability_type': 'prompt',
            'template_content': 'Updated template with {{variable}}',
            'description': 'Updated prompt',
            'access_control': 'public'
        }
        
        response = auth_client.put(
            f'/api/capabilities/{prompt_cap.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Verify capability was updated
        updated_cap = db.session.get(Capability, prompt_cap.id)
        assert updated_cap.template_content == 'Updated template with {{variable}}'
        assert updated_cap.global_resource_id is None
        
        # Verify NO new Resource record was created
        final_resource_count = Resource.query.count()
        assert final_resource_count == initial_resource_count
    
    def test_update_resource_capability_creates_resource_record(self, auth_client, db, sample_service_for_prompt):
        """Test that updating a resource capability with new content creates a Resource record"""
        # Create initial resource capability
        resource_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='initial_resource',
            capability_type='resource',
            description='Initial resource',
            is_enabled=True
        )
        db.session.add(resource_cap)
        db.session.commit()
        
        initial_resource_count = Resource.query.count()
        
        # Update resource capability with new content
        data = {
            'name': 'updated_resource',
            'capability_type': 'resource',
            'resource_uri': 'test://updated/resource',
            'template_content': 'Updated resource content',
            'description': 'Updated resource',
            'access_control': 'public'
        }
        
        response = auth_client.put(
            f'/api/capabilities/{resource_cap.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Verify capability was updated with global_resource_id
        updated_cap = db.session.get(Capability, resource_cap.id)
        assert updated_cap.global_resource_id is not None
        
        # Verify a new Resource record WAS created
        final_resource_count = Resource.query.count()
        assert final_resource_count == initial_resource_count + 1


class TestPromptsGetEndpoint:
    """Test prompts/get MCP endpoint functionality"""
    
    def test_prompts_get_with_template_content(self, auth_client, db, sample_service_for_prompt, sample_connection_account):
        """Test prompts/get returns template_content when it exists"""
        # Create prompt capability with template_content
        prompt_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='test_prompt_with_content',
            capability_type='prompt',
            template_content='Hello {{name}}, welcome!',
            description='Test prompt with content',
            is_enabled=True
        )
        db.session.add(prompt_cap)
        db.session.commit()
        
        # Make MCP prompts/get request
        mcp_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'prompts/get',
            'params': {
                'name': 'test_prompt_with_content'
            }
        }
        
        response = auth_client.post(
            f'/{sample_service_for_prompt.mcp_service.identifier}/mcp',
            data=json.dumps(mcp_request),
            content_type='application/json',
            headers={'Authorization': f'Bearer {sample_connection_account.bearer_token}'}
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert 'result' in result
        assert 'messages' in result['result']
        assert len(result['result']['messages']) > 0
        
        # Verify the template content is in the message
        message_text = result['result']['messages'][0]['content']['text']
        assert 'Hello {{name}}, welcome!' in message_text or 'Hello' in message_text
    
    def test_prompts_get_with_resource_fallback(self, auth_client, db, sample_service_for_prompt, sample_global_resource, sample_connection_account):
        """Test prompts/get fallback to Resource table when template_content is null"""
        # Create prompt capability with global_resource_id but no template_content
        prompt_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='test_prompt_with_resource',
            capability_type='prompt',
            template_content=None,  # Null template_content
            global_resource_id=sample_global_resource.id,  # Points to Resource
            description='Test prompt with resource fallback',
            is_enabled=True
        )
        db.session.add(prompt_cap)
        db.session.commit()
        
        # Make MCP prompts/get request
        mcp_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'prompts/get',
            'params': {
                'name': 'test_prompt_with_resource'
            }
        }
        
        response = auth_client.post(
            f'/{sample_service_for_prompt.mcp_service.identifier}/mcp',
            data=json.dumps(mcp_request),
            content_type='application/json',
            headers={'Authorization': f'Bearer {sample_connection_account.bearer_token}'}
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert 'result' in result
        assert 'messages' in result['result']
        assert len(result['result']['messages']) > 0
        
        # Verify the content from Resource table is returned
        message_text = result['result']['messages'][0]['content']['text']
        # The resource content is: 'Hello {{name}}, you are {{role}}.'
        assert 'Hello' in message_text


class TestCapabilityListAPI:
    """Test capability list API returns correct data for different types"""
    
    def test_capability_list_includes_all_types(self, auth_client, db, sample_service_for_prompt, sample_global_resource):
        """Test that capability list API returns all capability types with correct data"""
        # Create capabilities of different types
        tool_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='test_tool',
            capability_type='tool',
            url='https://api.example.com/tool',
            description='Test tool',
            is_enabled=True
        )
        
        mcp_tool_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='test_mcp_tool',
            capability_type='mcp_tool',
            url='mcp://service/tool',
            description='Test MCP tool',
            is_enabled=True
        )
        
        prompt_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='test_prompt',
            capability_type='prompt',
            template_content='Test prompt {{var}}',
            description='Test prompt',
            is_enabled=True
        )
        
        resource_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='test_resource',
            capability_type='resource',
            global_resource_id=sample_global_resource.id,
            description='Test resource',
            is_enabled=True
        )
        
        db.session.add_all([tool_cap, mcp_tool_cap, prompt_cap, resource_cap])
        db.session.commit()
        
        # Get capability list
        response = auth_client.get(f'/api/apps/{sample_service_for_prompt.id}/capabilities')
        
        assert response.status_code == 200
        capabilities = json.loads(response.data)
        
        assert len(capabilities) == 4
        
        # Verify each capability type is present
        cap_types = {cap['capability_type'] for cap in capabilities}
        assert 'tool' in cap_types
        assert 'mcp_tool' in cap_types
        assert 'prompt' in cap_types
        assert 'resource' in cap_types
        
        # Verify tool and mcp_tool have URL
        for cap in capabilities:
            if cap['capability_type'] in ['tool', 'mcp_tool']:
                assert 'url' in cap
                assert cap['url'] is not None
            else:
                # prompt and resource may not have URL or it may be null
                assert cap['capability_type'] in ['prompt', 'resource']
    
    def test_capability_detail_returns_correct_fields_for_prompt(self, auth_client, db, sample_service_for_prompt):
        """Test that capability detail API returns correct fields for prompt type"""
        # Create prompt capability
        prompt_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='detail_test_prompt',
            capability_type='prompt',
            template_content='Detail test {{variable}}',
            description='Detail test prompt',
            is_enabled=True
        )
        db.session.add(prompt_cap)
        db.session.commit()
        
        # Get capability detail
        response = auth_client.get(f'/api/capabilities/{prompt_cap.id}')
        
        assert response.status_code == 200
        capability = json.loads(response.data)
        
        assert capability['capability_type'] == 'prompt'
        assert 'template_content' in capability
        assert capability['template_content'] == 'Detail test {{variable}}'
        assert capability['global_resource_id'] is None
    
    def test_capability_detail_returns_correct_fields_for_resource(self, auth_client, db, sample_service_for_prompt, sample_global_resource):
        """Test that capability detail API returns correct fields for resource type"""
        # Create resource capability
        resource_cap = Capability(
            app_id=sample_service_for_prompt.id,
            name='detail_test_resource',
            capability_type='resource',
            global_resource_id=sample_global_resource.id,
            description='Detail test resource',
            is_enabled=True
        )
        db.session.add(resource_cap)
        db.session.commit()
        
        # Get capability detail
        response = auth_client.get(f'/api/capabilities/{resource_cap.id}')
        
        assert response.status_code == 200
        capability = json.loads(response.data)
        
        assert capability['capability_type'] == 'resource'
        assert 'global_resource_id' in capability
        assert capability['global_resource_id'] == sample_global_resource.id
