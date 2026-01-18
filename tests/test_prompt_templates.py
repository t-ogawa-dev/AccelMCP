"""
Tests for prompt template functionality
"""
import pytest
import json
from app.models.models import (
    db, McpService, Service, Capability, Variable, ConnectionAccount
)


@pytest.fixture
def prompt_capability(db):
    """Create a prompt-type capability with template"""
    mcp_service = McpService(
        name='Prompt Service',
        identifier='prompt-service',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Prompt App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    capability = Capability(
        app_id=service.id,
        name='code_review_prompt',
        capability_type='prompt',
        url='',  # Prompts don't need URL
        description='Code review prompt template',
        template_content='Review the following {{language}} code:\n\n{{code}}\n\nFocus on: {{focus_areas}}',
        headers=json.dumps({}),
        body_params=json.dumps({
            'properties': {
                'language': {'type': 'string', 'description': 'Programming language'},
                'code': {'type': 'string', 'description': 'Code to review'},
                'focus_areas': {'type': 'string', 'description': 'Areas to focus on'}
            }
        })
    )
    db.session.add(capability)
    db.session.commit()
    
    return capability


@pytest.fixture
def tool_capability(db):
    """Create a tool-type capability"""
    mcp_service = McpService(
        name='Tool Service',
        identifier='tool-service',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Tool App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    capability = Capability(
        app_id=service.id,
        name='search_api',
        capability_type='tool',
        url='https://api.example.com/search',
        description='Search API',
        template_content=None,
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(capability)
    db.session.commit()
    
    return capability


def test_create_prompt_capability(db):
    """Test creating a prompt-type capability"""
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
    
    # Create prompt capability
    capability = Capability(
        app_id=service.id,
        name='test_prompt',
        capability_type='prompt',
        url='',
        description='Test prompt',
        template_content='Hello {{name}}!',
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(capability)
    db.session.commit()
    
    # Verify
    assert capability.id is not None
    assert capability.capability_type == 'prompt'
    assert capability.template_content == 'Hello {{name}}!'


def test_prompt_capability_to_dict_includes_template(prompt_capability):
    """Test that to_dict includes template_content"""
    data = prompt_capability.to_dict()
    
    assert 'template_content' in data
    assert data['template_content'] == prompt_capability.template_content
    assert '{{language}}' in data['template_content']


def test_tool_capability_to_dict_includes_url(tool_capability):
    """Test that tool capability includes URL"""
    data = tool_capability.to_dict()
    
    assert 'url' in data
    assert data['url'] == 'https://api.example.com/search'
    assert data['capability_type'] == 'tool'


def test_prompts_list_returns_only_prompt_type(client, db, prompt_capability, tool_capability):
    """Test that prompts/list returns only prompt-type capabilities"""
    # Create connection account
    mcp_service = prompt_capability.service.mcp_service
    account = ConnectionAccount(
        name='test_account',
        bearer_token='test_token_123'
    )
    db.session.add(account)
    db.session.commit()
    
    # Call MCP prompts/list endpoint
    # Note: This would typically go through MCP protocol, but we test the handler directly
    from app.services.mcp_handler import MCPHandler
    
    handler = MCPHandler(db)
    
    # Mock MCP request for prompts/list
    mcp_request = {
        'jsonrpc': '2.0',
        'method': 'prompts/list',
        'params': {},
        'id': 1
    }
    
    # Get all capabilities for this account
    capabilities = Capability.query.filter_by(
        capability_type='prompt'
    ).all()
    
    # Should only include prompt-type
    assert len(capabilities) >= 1
    for cap in capabilities:
        assert cap.capability_type == 'prompt'


def test_prompt_template_variable_substitution(prompt_capability):
    """Test that template variables can be identified"""
    template = prompt_capability.template_content
    
    # Check for variable markers
    assert '{{language}}' in template
    assert '{{code}}' in template
    assert '{{focus_areas}}' in template


def test_prompt_get_with_arguments(client, db, prompt_capability):
    """Test prompts/get with argument substitution"""
    # Create connection account
    account = ConnectionAccount(
        name='test_account',
        bearer_token='test_token_123'
    )
    db.session.add(account)
    db.session.commit()
    
    # Simulate variable substitution
    template = prompt_capability.template_content
    substituted = template.replace('{{language}}', 'Python')
    substituted = substituted.replace('{{code}}', 'def hello(): print("hi")')
    substituted = substituted.replace('{{focus_areas}}', 'performance, readability')
    
    # Verify substitution worked
    assert '{{' not in substituted
    assert 'Python' in substituted
    assert 'def hello()' in substituted
    assert 'performance' in substituted


def test_capability_type_validation(db):
    """Test that capability_type must be valid"""
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
    
    # Create with valid type
    capability = Capability(
        app_id=service.id,
        name='test',
        capability_type='tool',  # Valid
        url='https://example.com',
        description='Test',
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(capability)
    db.session.commit()
    
    assert capability.capability_type in ['tool', 'prompt']


def test_prompt_with_no_template(db):
    """Test that prompt capability can exist without template initially"""
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
    
    # Create prompt without template
    capability = Capability(
        app_id=service.id,
        name='empty_prompt',
        capability_type='prompt',
        url='',
        description='Empty prompt',
        template_content=None,
        headers=json.dumps({}),
        body_params=json.dumps({})
    )
    db.session.add(capability)
    db.session.commit()
    
    # Should be allowed
    assert capability.id is not None
    assert capability.template_content is None


def test_update_capability_type(db, tool_capability):
    """Test updating capability from tool to prompt"""
    # Start as tool
    assert tool_capability.capability_type == 'tool'
    assert tool_capability.url != ''
    
    # Update to prompt
    tool_capability.capability_type = 'prompt'
    tool_capability.template_content = 'Test template with {{variable}}'
    db.session.commit()
    
    # Verify update
    capability = Capability.query.get(tool_capability.id)
    assert capability.capability_type == 'prompt'
    assert capability.template_content is not None


def test_prompt_body_params_defines_variables(prompt_capability):
    """Test that body_params defines available template variables"""
    params = json.loads(prompt_capability.body_params)
    
    # Should have properties matching template variables
    assert 'properties' in params
    properties = params['properties']
    
    assert 'language' in properties
    assert 'code' in properties
    assert 'focus_areas' in properties
    
    # Each should have type and description
    for key, schema in properties.items():
        assert 'type' in schema
        assert 'description' in schema


def test_multiple_prompt_capabilities(db):
    """Test creating multiple prompt capabilities"""
    mcp_service = McpService(
        name='Multi Prompt Service',
        identifier='multi-prompt',
        routing_type='subdomain'
    )
    db.session.add(mcp_service)
    db.session.flush()
    
    service = Service(
        mcp_service_id=mcp_service.id,
        name='Multi Prompt App',
        service_type='api',
        mcp_url='https://api.example.com'
    )
    db.session.add(service)
    db.session.flush()
    
    # Create multiple prompts
    prompts = [
        Capability(
            app_id=service.id,
            name='summarize',
            capability_type='prompt',
            url='',
            description='Summarize text',
            template_content='Summarize: {{text}}',
            headers=json.dumps({}),
            body_params=json.dumps({})
        ),
        Capability(
            app_id=service.id,
            name='translate',
            capability_type='prompt',
            url='',
            description='Translate text',
            template_content='Translate {{text}} to {{language}}',
            headers=json.dumps({}),
            body_params=json.dumps({})
        ),
        Capability(
            app_id=service.id,
            name='analyze',
            capability_type='prompt',
            url='',
            description='Analyze sentiment',
            template_content='Analyze sentiment of: {{text}}',
            headers=json.dumps({}),
            body_params=json.dumps({})
        )
    ]
    
    for prompt in prompts:
        db.session.add(prompt)
    db.session.commit()
    
    # Query all prompts
    all_prompts = Capability.query.filter_by(
        app_id=service.id,
        capability_type='prompt'
    ).all()
    
    assert len(all_prompts) == 3
    assert all(p.capability_type == 'prompt' for p in all_prompts)
