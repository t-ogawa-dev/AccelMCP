"""
MCP Handler Service
Handles MCP requests with permission checking and API/MCP relay
"""
import json
import httpx
import re
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
    
    def _sanitize_tool_name(self, name: str) -> str:
        """
        Sanitize tool name to comply with Google API requirements:
        - Must start with a letter or underscore
        - Only alphanumeric, underscores, dots, colons, dashes
        - Max 64 characters
        """
        # Replace spaces and other invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_.:+-]', '_', name)
        
        # Ensure it starts with a letter or underscore
        if sanitized and not re.match(r'^[a-zA-Z_]', sanitized):
            sanitized = '_' + sanitized
        
        # Limit to 64 characters
        return sanitized[:64]
    
    def handle_mcp_service_request(self, account, mcp_service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request at MCP Service level (統合エンドポイント)
        
        Args:
            account: ConnectionAccount object
            mcp_service: McpService object
            mcp_request: MCP protocol request
        
        Returns:
            MCP protocol response
        """
        from app.models.models import Service
        
        method = mcp_request.get('method')
        
        if method == 'initialize':
            return self._handle_initialize_for_mcp_service(account, mcp_service, mcp_request)
        
        elif method == 'tools/list':
            return self._handle_tools_list_for_mcp_service(account, mcp_service, mcp_request)
        
        elif method == 'tools/call':
            return self._handle_tool_call_for_mcp_service(account, mcp_service, mcp_request)
        
        elif method == 'resources/list':
            return self._handle_resources_list(mcp_request)
        
        elif method == 'prompts/list':
            return self._handle_prompts_list(mcp_request)
        
        else:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32601,
                    'message': f'Method not found: {method}'
                }
            }
    
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
            # If restricted but no account, deny access
            if account is None:
                logger.debug("No account provided for restricted MCP Service")
                return False
                
            has_service_permission = self.db.session.query(AccountPermission).filter(
                AccountPermission.account_id == account.id,
                AccountPermission.mcp_service_id == mcp_service.id
            ).first() is not None
            
            if not has_service_permission:
                logger.debug(f"Account {account.id} denied: no MCP Service permission")
                return False
        
        # Level 2: App access control (if checking app or capability)
        if app and app.access_control == 'restricted':
            # If restricted but no account, deny access
            if account is None:
                logger.debug("No account provided for restricted App")
                return False
                
            has_app_permission = self.db.session.query(AccountPermission).filter(
                AccountPermission.account_id == account.id,
                AccountPermission.app_id == app.id
            ).first() is not None
            
            if not has_app_permission:
                logger.debug(f"Account {account.id} denied: no App permission")
                return False
        
        # Level 3: Capability access control (if checking specific capability)
        if capability and capability.access_control == 'restricted':
            # If restricted but no account, deny access
            if account is None:
                logger.debug("No account provided for restricted Capability")
                return False
                
            has_capability_permission = self.db.session.query(AccountPermission).filter(
                AccountPermission.account_id == account.id,
                AccountPermission.capability_id == capability.id
            ).first() is not None
            
            if not has_capability_permission:
                logger.debug(f"Account {account.id} denied: no Capability permission")
                return False
        
        # Log access granted
        if account:
            logger.debug(f"Account {account.id} granted access")
        else:
            logger.debug("Public access granted (no authentication required)")
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
                
                # Add body_params as input schema (preserve full schema including enums, descriptions, etc.)
                if cap.body_params:
                    try:
                        body_params = json.loads(cap.body_params)
                        # Use the complete schema from body_params if it has the right structure
                        if 'properties' in body_params:
                            # Remove _fixed field before sending to LLM (it's for internal use)
                            schema = {k: v for k, v in body_params.items() if k != '_fixed'}
                            tool['inputSchema'] = schema
                        else:
                            # Fallback: treat as simple key-value params
                            for key, value in body_params.items():
                                tool['inputSchema']['properties'][key] = {
                                    'type': 'string',
                                    'description': f'Parameter: {key}'
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
        
        if method == 'initialize':
            return self._handle_initialize(account, service, mcp_request)
        
        elif method == 'tools/list':
            return self._handle_tools_list(account, service)
        
        elif method == 'tools/call':
            return self._handle_tool_call(account, service, mcp_request)
        
        elif method == 'resources/list':
            return self._handle_resources_list(mcp_request)
        
        elif method == 'prompts/list':
            return self._handle_prompts_list(mcp_request)
        
        else:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32601,
                    'message': f'Method not found: {method}'
                }
            }
    
    def _handle_initialize_for_mcp_service(self, account, mcp_service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request at MCP Service level"""
        import uuid
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {
                    'tools': {},
                    'resources': {},
                    'prompts': {}
                },
                'serverInfo': {
                    'name': f'AccelMCP - {mcp_service.name}',
                    'version': '1.0.0'
                },
                'sessionId': str(uuid.uuid4())
            }
        }
    
    def _handle_tools_list_for_mcp_service(self, account, mcp_service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Return aggregated tools list from all apps under MCP Service"""
        from app.models.models import Service, Capability
        
        # Check hierarchical access at MCP service level
        if not self._check_hierarchical_access(account, mcp_service):
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'result': {
                    'tools': []  # Return empty if no access to MCP service
                }
            }
        
        # Get all apps under this MCP service
        apps = self.db.session.query(Service).filter(
            Service.mcp_service_id == mcp_service.id
        ).all()
        
        # Aggregate tools from all apps
        all_tools = []
        for app in apps:
            # Check app-level access
            if not self._check_hierarchical_access(account, mcp_service, app=app):
                continue
            
            # Get all capabilities for this app
            capabilities = self.db.session.query(Capability).filter(
                Capability.app_id == app.id
            ).all()
            
            for cap in capabilities:
                # Check capability-level access
                if not self._check_hierarchical_access(account, mcp_service, app=app, capability=cap):
                    continue
                
                # Use namespace: app_name:capability_name (sanitized for Google API)
                sanitized_app_name = self._sanitize_tool_name(app.name)
                sanitized_cap_name = self._sanitize_tool_name(cap.name)
                tool_name = f"{sanitized_app_name}:{sanitized_cap_name}"
                
                tool = {
                    'name': tool_name,
                    'description': cap.description or f'{cap.capability_type.upper()} tool: {cap.name} (from {app.name})',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                }
                
                # Add body_params as input schema (preserve full schema including enums, descriptions, etc.)
                if cap.body_params:
                    try:
                        body_params = json.loads(cap.body_params)
                        # Use the complete schema from body_params if it has the right structure
                        if 'properties' in body_params:
                            # Remove _fixed field before sending to LLM (it's for internal use)
                            schema = {k: v for k, v in body_params.items() if k != '_fixed'}
                            tool['inputSchema'] = schema
                        else:
                            # Fallback: treat as simple key-value params
                            for key, value in body_params.items():
                                tool['inputSchema']['properties'][key] = {
                                    'type': 'string',
                                    'description': f'Parameter: {key}'
                                }
                    except json.JSONDecodeError:
                        pass
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'tools': all_tools
            }
        }
    
    def _handle_tool_call_for_mcp_service(self, account, mcp_service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool call at MCP Service level with namespace support"""
        from app.models.models import Service, Capability
        
        params = mcp_request.get('params', {})
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        app = None
        capability = None
        
        # Parse tool name: app_name:capability_name or simple capability_name
        if ':' in tool_name:
            # Namespaced format
            sanitized_app_name, sanitized_cap_name = tool_name.split(':', 1)
            
            # Find app by matching sanitized name
            all_apps = self.db.session.query(Service).filter(
                Service.mcp_service_id == mcp_service.id
            ).all()
            
            for a in all_apps:
                if self._sanitize_tool_name(a.name) == sanitized_app_name:
                    app = a
                    # Find capability by matching sanitized name
                    all_caps = self.db.session.query(Capability).filter(
                        Capability.app_id == app.id
                    ).all()
                    for c in all_caps:
                        if self._sanitize_tool_name(c.name) == sanitized_cap_name:
                            capability = c
                            break
                    break
        else:
            # Simple format: search across all apps
            apps = self.db.session.query(Service).filter(
                Service.mcp_service_id == mcp_service.id
            ).all()
            
            for a in apps:
                cap = self.db.session.query(Capability).filter(
                    Capability.app_id == a.id,
                    Capability.name == tool_name
                ).first()
                if cap:
                    app = a
                    capability = cap
                    break
        
        if not capability or not app:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32602,
                    'message': f'Tool not found: {tool_name}'
                }
            }
        
        # Check hierarchical permission
        if not self._check_hierarchical_access(account, mcp_service, app=app, capability=capability):
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32000,
                    'message': f'Permission denied for tool: {tool_name}'
                }
            }
        
        # Execute capability
        if capability.capability_type == 'api':
            result = self._execute_api_call(app, capability, arguments)
        elif capability.capability_type in ('mcp', 'mcp_tool'):
            result = self._execute_mcp_call(app, capability, arguments)
        else:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32603,
                    'message': f'Unknown capability type: {capability.capability_type}'
                }
            }
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'content': [
                    {
                        'type': 'text',
                        'text': json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    def _handle_initialize(self, account, service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        import uuid
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {
                    'tools': {},
                    'resources': {},
                    'prompts': {}
                },
                'serverInfo': {
                    'name': f'AccelMCP - {service.name}',
                    'version': '1.0.0'
                },
                'sessionId': str(uuid.uuid4())
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
                
                # Add body_params as input schema (preserve full schema including enums, descriptions, etc.)
                if cap.body_params:
                    try:
                        body_params = json.loads(cap.body_params)
                        # Use the complete schema from body_params if it has the right structure
                        if 'properties' in body_params:
                            # Remove _fixed field before sending to LLM (it's for internal use)
                            schema = {k: v for k, v in body_params.items() if k != '_fixed'}
                            tool['inputSchema'] = schema
                        else:
                            # Fallback: treat as simple key-value params
                            for key, value in body_params.items():
                                tool['inputSchema']['properties'][key] = {
                                    'type': 'string',
                                    'description': f'Parameter: {key}'
                                }
                    except json.JSONDecodeError:
                        pass
                
                tools.append(tool)
        
        return {
            'jsonrpc': '2.0',
            'id': 0,
            'result': {
                'tools': tools
            }
        }
    
    def _handle_resources_list(self, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request (stub implementation)"""
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'resources': []
            }
        }
    
    def _handle_prompts_list(self, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request (stub implementation)"""
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'prompts': []
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
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32602,
                    'message': f'Tool not found: {tool_name}'
                }
            }
        
        # Check hierarchical permission
        if not self._check_hierarchical_access(account, mcp_service, app=service, capability=capability):
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
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
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32603,
                    'message': f'Unknown capability type: {capability.type}'
                }
            }
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
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
        fixed_params = {}
        
        if capability.body_params:
            # body_params can be string (JSON) or dict
            body_params = capability.body_params
            if isinstance(body_params, str):
                # JSON string: parse it
                try:
                    parsed = json.loads(body_params)
                    
                    # Check if it's new format with JSON Schema structure
                    if 'properties' in parsed and '_fixed' in parsed:
                        # New format: extract fixed params and prepare for LLM arguments
                        fixed_params = parsed.get('_fixed', {})
                        # Properties define the schema for LLM arguments
                        # The actual values come from 'arguments'
                    elif 'properties' in parsed:
                        # JSON Schema without fixed params (MCP auto-discovered)
                        # Schema only, no fixed params
                        pass
                    else:
                        # Old format: simple key-value, treat as fixed params
                        fixed_params = parsed
                    
                    # Replace variables in fixed params
                    fixed_params = VariableReplacer.replace_in_dict(fixed_params)
                except (json.JSONDecodeError, TypeError):
                    pass
            else:
                # Dict: parse and replace
                try:
                    parsed = json.loads(body_params)
                    if 'properties' in parsed and '_fixed' in parsed:
                        fixed_params = parsed.get('_fixed', {})
                        fixed_params = VariableReplacer.replace_in_dict(fixed_params)
                    elif 'properties' in parsed:
                        pass  # Schema only
                    else:
                        fixed_params = VariableReplacer.replace_in_body_params(parsed)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Start with fixed params, then merge LLM-provided arguments
        body.update(fixed_params)
        body.update(arguments)
        
        # Check HTTP method from headers
        http_method = headers.get('X-HTTP-Method', 'POST').upper()
        
        try:
            # Make HTTP request
            if http_method == 'GET':
                # For GET, use query parameters instead of body
                response = httpx.get(
                    url,
                    params=body,  # Query parameters
                    headers=headers,
                    timeout=30.0
                )
            else:
                # POST or other methods
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
            
            # For mcp_tool type, use service.mcp_url (capability.service is the Service/App model)
            app = capability.service
            mcp_url = app.mcp_url if app else capability.url
            
            if not mcp_url:
                return {
                    'success': False,
                    'error': 'MCP server URL is not configured'
                }
            
            if mcp_url.startswith('http'):
                # HTTP MCP connection
                headers = {}
                if service.common_headers:
                    headers.update(json.loads(service.common_headers))
                if capability.headers:
                    headers.update(json.loads(capability.headers))
                
                # Add depth header for daisy-chain loop prevention
                from flask import request
                current_depth = int(request.headers.get('X-AccelMCP-Depth', '0'))
                max_depth = 10  # Maximum daisy-chain depth
                
                if current_depth >= max_depth:
                    return {
                        'success': False,
                        'error': f'Maximum MCP daisy-chain depth ({max_depth}) exceeded'
                    }
                
                headers['X-AccelMCP-Depth'] = str(current_depth + 1)
                
                # Check if we need to establish a session (GitHub Copilot MCP requires session)
                if 'Mcp-Session-Id' not in headers:
                    # Send initialize request to establish session
                    init_request = {
                        'jsonrpc': '2.0',
                        'id': 0,
                        'method': 'initialize',
                        'params': {
                            'protocolVersion': '2024-11-05',
                            'capabilities': {},
                            'clientInfo': {
                                'name': 'AccelMCP',
                                'version': '1.0.0'
                            }
                        }
                    }
                    
                    logger.debug(f"Initializing MCP session at {mcp_url}")
                    init_response = httpx.post(
                        mcp_url,
                        headers=headers,
                        json=init_request,
                        timeout=30.0
                    )
                    init_response.raise_for_status()
                    
                    # Extract session ID from response headers
                    session_id = init_response.headers.get('Mcp-Session-Id')
                    if session_id:
                        headers['Mcp-Session-Id'] = session_id
                        logger.debug(f"MCP session established: {session_id}")
                
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
                
                logger.debug(f"Sending MCP request to {mcp_url}: {json.dumps(mcp_request, indent=2)}")
                logger.debug(f"Request headers: {headers}")
                
                response = httpx.post(
                    mcp_url,
                    headers=headers,
                    json=mcp_request,
                    timeout=30.0
                )
                
                logger.debug(f"MCP response status: {response.status_code}, body: {response.text}")
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
