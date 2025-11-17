"""
MCP Handler Service
Handles MCP requests with permission checking and API/MCP relay
"""
import json
import httpx
from typing import Dict, Any, List
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPHandler:
    """Handle MCP requests with permission checking and API/MCP relay"""
    
    def __init__(self, db):
        self.db = db
    
    def get_capabilities(self, account, service) -> Dict[str, Any]:
        """
        Get user's available capabilities for a service
        Used for GET /mcp endpoint
        
        Args:
            user: ConnectionAccount object
            service: Service object
        
        Returns:
            MCP capabilities response
        """
        from app.models.models import Capability, AccountPermission
        
        # Get capabilities user has permission for
        permitted_capabilities = self.db.session.query(Capability).join(
            AccountPermission
        ).filter(
            AccountPermission.account_id == account.id,
            Capability.service_id == service.id
        ).all()
        
        tools = []
        for cap in permitted_capabilities:
            tool = {
                'name': cap.name,
                'description': cap.description or f'{cap.type.upper()} tool: {cap.name}',
                'inputSchema': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
            
            # Add body_params as input schema
            if cap.body_params:
                try:
                    body_params = json.loads(cap.body_params)
                    for key, value in body_params.items():
                        tool['inputSchema']['properties'][key] = {
                            'type': 'string',
                            'description': f'Parameter: {key}',
                            'default': value
                        }
                except json.JSONDecodeError:
                    pass
            
            tools.append(tool)
        
        return {
            'capabilities': {
                'tools': tools
            },
            'serverInfo': {
                'name': service.name,
                'version': '1.0.0'
            }
        }
    
    def execute_tool_by_id(self, account, service, tool_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool by its ID (name or capability ID)
        Used for POST /tools/<tool_id> endpoint
        
        Args:
            user: ConnectionAccount object
            service: Service object
            tool_id: Tool identifier (capability name or ID)
            arguments: Tool arguments
        
        Returns:
            MCP tool execution response
        """
        from app.models.models import Capability, AccountPermission
        
        # Try to find capability by name first, then by ID
        capability = self.db.session.query(Capability).filter(
            Capability.service_id == service.id,
            (Capability.name == tool_id) | (Capability.id == tool_id)
        ).first()
        
        if not capability:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': f'Tool not found: {tool_id}'
                }
            }
        
        # Check permission
        permission = self.db.session.query(AccountPermission).filter(
            AccountPermission.account_id == account.id,
            AccountPermission.capability_id == capability.id
        ).first()
        
        if not permission:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': f'Permission denied for tool: {capability.name}'
                }
            }
        
        # Execute capability
        if capability.type == 'api':
            result = self._execute_api_call(service, capability, arguments)
        elif capability.type == 'mcp':
            result = self._execute_mcp_call(service, capability, arguments)
        else:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': f'Unknown capability type: {capability.type}'
                }
            }
        
        # Return MCP-compliant response
        return {
            'content': [
                {
                    'type': 'text',
                    'text': json.dumps(result, ensure_ascii=False, indent=2)
                }
            ],
            'isError': not result.get('success', True)
        }
    
    def handle_http_request(self, account, service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle HTTP MCP request
        
        Args:
            user: ConnectionAccount object
            service: Service object
            mcp_request: MCP protocol request
        
        Returns:
            MCP protocol response
        """
        method = mcp_request.get('method')
        
        if method == 'tools/list':
            return self._handle_tools_list(account, service)
        
        elif method == 'tools/call':
            return self._handle_tool_call(account, service, mcp_request)
        
        else:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id'),
                'error': {
                    'code': -32601,
                    'message': f'Method not found: {method}'
                }
            }
    
    def _handle_tools_list(self, account, service) -> Dict[str, Any]:
        """Return list of tools user has permission to use"""
        from app.models.models import Capability, AccountPermission
        
        # Get capabilities user has permission for
        permitted_capabilities = self.db.session.query(Capability).join(
            AccountPermission
        ).filter(
            AccountPermission.account_id == account.id,
            Capability.service_id == service.id
        ).all()
        
        tools = []
        for cap in permitted_capabilities:
            tool = {
                'name': cap.name,
                'description': cap.description or f'{cap.type.upper()} tool: {cap.name}',
                'inputSchema': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
            
            # Add body_params as input schema
            if cap.body_params:
                body_params = json.loads(cap.body_params)
                for key, value in body_params.items():
                    tool['inputSchema']['properties'][key] = {
                        'type': 'string',
                        'description': f'Parameter: {key}'
                    }
            
            tools.append(tool)
        
        return {
            'jsonrpc': '2.0',
            'result': {
                'tools': tools
            }
        }
    
    def _handle_tool_call(self, account, service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool call with permission check"""
        from app.models.models import Capability, AccountPermission
        
        params = mcp_request.get('params', {})
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        # Find capability
        capability = self.db.session.query(Capability).filter(
            Capability.service_id == service.id,
            Capability.name == tool_name
        ).first()
        
        if not capability:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id'),
                'error': {
                    'code': -32602,
                    'message': f'Tool not found: {tool_name}'
                }
            }
        
        # Check permission
        permission = self.db.session.query(AccountPermission).filter(
            AccountPermission.account_id == account.id,
            AccountPermission.capability_id == capability.id
        ).first()
        
        if not permission:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id'),
                'error': {
                    'code': -32603,
                    'message': f'Permission denied for tool: {tool_name}'
                }
            }
        
        # Execute capability
        if capability.type == 'api':
            result = self._execute_api_call(service, capability, arguments)
        elif capability.type == 'mcp':
            result = self._execute_mcp_call(service, capability, arguments)
        else:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id'),
                'error': {
                    'code': -32603,
                    'message': f'Unknown capability type: {capability.type}'
                }
            }
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id'),
            'result': {
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    def _execute_api_call(self, service, capability, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call"""
        # Merge headers: service common headers + capability specific headers
        headers = {}
        if service.common_headers:
            headers.update(json.loads(service.common_headers))
        if capability.headers:
            headers.update(json.loads(capability.headers))
        
        # Merge body params with arguments
        body = {}
        if capability.body_params:
            body.update(json.loads(capability.body_params))
        body.update(arguments)
        
        try:
            # Make HTTP request
            response = httpx.post(
                capability.url,
                headers=headers,
                json=body,
                timeout=30.0
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except httpx.HTTPError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_mcp_call(self, service, capability, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP relay call"""
        # For MCP relay, we need to connect to another MCP server
        # This is a placeholder - actual implementation would use MCP client
        
        try:
            # Parse MCP server URL
            # Expected format: http://host:port or mcp://command
            
            if capability.url.startswith('http'):
                # HTTP MCP connection
                headers = {}
                if service.common_headers:
                    headers.update(json.loads(service.common_headers))
                if capability.headers:
                    headers.update(json.loads(capability.headers))
                
                # Make MCP request
                mcp_request = {
                    'jsonrpc': '2.0',
                    'id': 1,
                    'method': 'tools/call',
                    'params': {
                        'name': capability.name,
                        'arguments': arguments
                    }
                }
                
                response = httpx.post(
                    capability.url,
                    headers=headers,
                    json=mcp_request,
                    timeout=30.0
                )
                response.raise_for_status()
                
                return response.json()
            
            else:
                # For stdio MCP, would need to spawn process
                return {
                    'success': False,
                    'error': 'stdio MCP relay not yet implemented'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
