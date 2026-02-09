#!/usr/bin/env python
from app import create_app
from app.models.models import McpService, Service, Capability
from app.services.mcp_handler import McpHandler

app = create_app()
with app.app_context():
    from app import db
    
    # Create test data
    mcp = McpService(
        name='Test MCP',
        identifier='auc',
        routing_type='subdomain',
        access_control='public',
        is_enabled=True
    )
    db.session.add(mcp)
    db.session.commit()
    
    service = Service(
        name='Weather API',
        service_type='api',
        mcp_url='https://api.example.com',
        mcp_service_id=mcp.id,
        is_enabled=True,
        access_control='public'
    )
    db.session.add(service)
    db.session.commit()
    
    cap = Capability(
        name='get_weather',
        description='Get weather forecast',
        capability_type='tool',
        app_id=service.id,
        url='https://httpbin.org/post',
        is_enabled=True,
        access_control='public'
    )
    db.session.add(cap)
    db.session.commit()
    
    # Test tools/list
    handler = McpHandler(db)
    result = handler._handle_tools_list_for_mcp_service(None, mcp, {'id': 1})
    
    print('=== Generated tool names ===')
    for tool in result['result']['tools']:
        print(f'Tool name: {tool["name"]}')
        print(f'Description: {tool["description"]}')
        print()
    
    # Cleanup
    db.session.delete(cap)
    db.session.delete(service)
    db.session.delete(mcp)
    db.session.commit()

print('Format: {mcp_identifier}_{app_name}:{capability_name}')
print('Example: auc_Weather_API:get_weather')
