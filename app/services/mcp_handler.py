"""
MCP Handler Service
Handles MCP requests with permission checking and API/MCP relay
"""
import json
import httpx
from typing import Dict, Any, List, Optional
import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPHandler:
    """Handle MCP requests with permission checking and API/MCP relay"""
    
    def __init__(self, db):
        self.db = db
    
    def _check_hierarchical_access(self, account, mcp_service, app=None, capability=None) -> bool:
        """
        Check if account has access using 3-tier hierarchical model
        
        Access hierarchy:
        1. McpService level: Check if service.access_control=='restricted' and permission exists
        2. App level: Check if app.access_control=='restricted' and permission exists  
        3. Capability level: Check if capability.access_control=='restricted' and permission exists
        
        Also checks is_enabled flags at each level.
        
        Args:
            account: ConnectionAccount object
            mcp_service: McpService object
            app: Service (App) object (optional)
            capability: Capability object (optional)
            
        Returns:
            True if access granted, False otherwise
        """
        from app.models.models import AccountPermission
        
        # Check is_enabled flags
        if not mcp_service.is_enabled:
            logger.warning(f"MCP Service {mcp_service.id} is disabled")
            return False
        
        if app and not app.is_enabled:
            logger.warning(f"App {app.id} is disabled")
            return False
            
        if capability and not capability.is_enabled:
            logger.warning(f"Capability {capability.id} is disabled")
            return False
        
        # Level 1: McpService access control
        if mcp_service.access_control == 'restricted':
            has_service_permission = self.db.session.query(AccountPermission).filter(
                AccountPermission.account_id == account.id,
                AccountPermission.mcp_service_id == mcp_service.id
            ).first() is not None
            
            if not has_service_permission:
                logger.debug(f"Account {account.id} denied: no MCP Service permission")
                return False
        
        # Level 2: App access control (if checking app or capability)
        if app and app.access_control == 'restricted':
            has_app_permission = self.db.session.query(AccountPermission).filter(
                AccountPermission.account_id == account.id,
                AccountPermission.app_id == app.id
            ).first() is not None
            
            if not has_app_permission:
                logger.debug(f"Account {account.id} denied: no App permission")
                return False
        
        # Level 3: Capability access control (if checking specific capability)
        if capability and capability.access_control == 'restricted':
            has_capability_permission = self.db.session.query(AccountPermission).filter(
                AccountPermission.account_id == account.id,
                AccountPermission.capability_id == capability.id
            ).first() is not None
            
            if not has_capability_permission:
                logger.debug(f"Account {account.id} denied: no Capability permission")
                return False
        
        logger.debug(f"Account {account.id} granted access")
        return True
    
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
        from app.models.models import Capability
        
        # Get mcp_service for hierarchical check
        mcp_service = service.mcp_service
        
        # Check hierarchical access at app level
        if not self._check_hierarchical_access(account, mcp_service, app=service):
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': 'Access denied to this service'
                }
            }
        
        # Get all capabilities for this service
        all_capabilities = self.db.session.query(Capability).filter(
            Capability.app_id == service.id
        ).all()
        
        # Filter capabilities based on hierarchical access
        tools = []
        for cap in all_capabilities:
            # Check if user has access to this specific capability
            if self._check_hierarchical_access(account, mcp_service, app=service, capability=cap):
                tool = {
                    'name': cap.name,
                    'description': cap.description or f'{cap.capability_type.upper()} tool: {cap.name}',
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
        from app.models.models import Capability
        
        # Get mcp_service for hierarchical check
        mcp_service = service.mcp_service
        
        # Try to find capability by name first, then by ID
        capability = self.db.session.query(Capability).filter(
            Capability.app_id == service.id,
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
        
        # Check hierarchical permission
        if not self._check_hierarchical_access(account, mcp_service, app=service, capability=capability):
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
        from app.models.models import Capability
        
        # Get mcp_service for hierarchical check
        mcp_service = service.mcp_service
        
        # Check if user has access to the service
        if not self._check_hierarchical_access(account, mcp_service, app=service):
            return {
                'jsonrpc': '2.0',
                'result': {
                    'tools': []  # Return empty list if no access to service
                }
            }
        
        # Get all capabilities for this service
        all_capabilities = self.db.session.query(Capability).filter(
            Capability.app_id == service.id
        ).all()
        
        # Filter capabilities based on hierarchical access
        tools = []
        for cap in all_capabilities:
            if self._check_hierarchical_access(account, mcp_service, app=service, capability=cap):
                tool = {
                    'name': cap.name,
                    'description': cap.description or f'{cap.capability_type.upper()} tool: {cap.name}',
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
        from app.models.models import Capability
        
        # Get mcp_service for hierarchical check
        mcp_service = service.mcp_service
        
        params = mcp_request.get('params', {})
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        # Find capability
        capability = self.db.session.query(Capability).filter(
            Capability.app_id == service.id,
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
        
        # Check hierarchical permission
        if not self._check_hierarchical_access(account, mcp_service, app=service, capability=capability):
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id'),
                'error': {
                    'code': -32000,
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
        from app.services.variable_replacer import VariableReplacer
        
        # Merge headers: service common headers + capability specific headers
        headers = {}
        if service.common_headers:
            headers.update(json.loads(service.common_headers))
        if capability.headers:
            headers.update(json.loads(capability.headers))
        
        # Replace variables in headers (always as strings)
        headers = VariableReplacer.replace_in_dict(headers)
        
        # Replace variables in URL (always as strings)
        url = VariableReplacer.replace_in_string(capability.url)
        
        # Merge body params with arguments
        body = {}
        if capability.body_params:
            # body_params can be string (JSON) or dict
            body_params = capability.body_params
            if isinstance(body_params, str):
                # JSON string: replace with type preservation
                body = VariableReplacer.replace_in_json(body_params)
                if not isinstance(body, dict):
                    body = {}
            else:
                # Dict: parse and replace
                try:
                    parsed = json.loads(body_params)
                    body = VariableReplacer.replace_in_body_params(parsed)
                except (json.JSONDecodeError, TypeError):
                    body = {}
        
        body.update(arguments)
        
        try:
            # Make HTTP request
            response = httpx.post(
                url,
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
