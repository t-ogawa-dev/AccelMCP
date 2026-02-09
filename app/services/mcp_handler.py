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
    
    def _convert_param_type(self, value: str, param_type: str):
        """
        Convert string value to specified type
        
        Args:
            value: String value (may contain {{VARIABLE}})
            param_type: Target type ('string', 'number', 'integer', 'boolean', 'object', 'array')
        
        Returns:
            Converted value with appropriate type
        """
        # If value contains variable placeholder, keep as string for now
        # Variable replacement happens later
        if '{{' in value and '}}' in value:
            return value
        
        if param_type == 'integer':
            try:
                return int(value)
            except (ValueError, AttributeError):
                return value  # Keep as string if conversion fails
        elif param_type == 'number':
            try:
                # Try to convert to float
                return float(value)
            except (ValueError, AttributeError):
                return value  # Keep as string if conversion fails
        elif param_type == 'boolean':
            # Convert to boolean
            return value.lower() in ('true', '1', 'yes', 'on')
        elif param_type == 'object':
            # Try to parse as JSON object
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
                return value
            except (json.JSONDecodeError, ValueError):
                return value
        elif param_type == 'array':
            # Try to parse as JSON array
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
                return value
            except (json.JSONDecodeError, ValueError):
                return value
        else:
            # Default: keep as string
            return value
    
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
            return self._handle_resources_list_for_mcp_service(account, mcp_service, mcp_request)
        
        elif method == 'resources/read':
            return self._handle_resources_read(account, mcp_request)
        
        elif method == 'prompts/list':
            return self._handle_prompts_list(mcp_request)
        
        elif method == 'prompts/get':
            return self._handle_prompts_get(mcp_request)
        
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
            return self._handle_resources_list_for_service(account, service, mcp_request)
        
        elif method == 'resources/read':
            return self._handle_resources_read(account, mcp_request)
        
        elif method == 'prompts/list':
            return self._handle_prompts_list(mcp_request)
        
        elif method == 'prompts/get':
            return self._handle_prompts_get(mcp_request)
        
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
        from app.models.models import Service, Capability
        
        # Check which capability types are actually registered
        apps = self.db.session.query(Service).filter(
            Service.mcp_service_id == mcp_service.id,
            Service.is_enabled == True
        ).all()
        
        has_tools = False
        has_resources = False
        has_prompts = False
        
        for app in apps:
            capability_types = self.db.session.query(Capability.capability_type).filter(
                Capability.app_id == app.id,
                Capability.is_enabled == True
            ).distinct().all()
            
            for (cap_type,) in capability_types:
                if cap_type in ['tool', 'mcp_tool']:
                    has_tools = True
                elif cap_type == 'resource':
                    has_resources = True
                elif cap_type == 'prompt':
                    has_prompts = True
        
        # Build capabilities dynamically based on what's registered
        capabilities = {}
        if has_tools:
            capabilities['tools'] = {}
        if has_resources:
            capabilities['resources'] = {}
        if has_prompts:
            capabilities['prompts'] = {}
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': capabilities,
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
            
            # Get all tool-type capabilities for this app (exclude resource and prompt types)
            capabilities = self.db.session.query(Capability).filter(
                Capability.app_id == app.id,
                Capability.capability_type.in_(['tool', 'mcp_tool']),
                Capability.is_enabled == True
            ).all()
            
            for cap in capabilities:
                # Check capability-level access
                if not self._check_hierarchical_access(account, mcp_service, app=app, capability=cap):
                    continue
                
                # Use namespace: mcp_identifier_app_name:capability_name (sanitized for Google API)
                mcp_prefix = self._sanitize_tool_name(mcp_service.identifier) if mcp_service.identifier else 'mcp'
                sanitized_app_name = self._sanitize_tool_name(app.name) if app.name else 'app'
                sanitized_cap_name = self._sanitize_tool_name(cap.name)
                # Fallback if sanitized name is empty or only special characters
                if not sanitized_app_name or sanitized_app_name.replace('_', '').replace(':', '').replace('-', '').replace('+', '').replace('.', '') == '':
                    sanitized_app_name = 'app'
                tool_name = f"{mcp_prefix}_{sanitized_app_name}:{sanitized_cap_name}"
                
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
                            # Send full schema to LLM (including const-constrained fixed params)
                            # const制約により、LLMはパラメータを認識するが値は変更できない
                            tool['inputSchema'] = {k: v for k, v in body_params.items()}
                        else:
                            # Fallback: treat as simple key-value params
                            for key, value in body_params.items():
                                tool['inputSchema']['properties'][key] = {
                                    'type': 'string',
                                    'description': f'Parameter: {key}'
                                }
                    except json.JSONDecodeError:
                        pass
                
                # Add tool to list
                all_tools.append(tool)
        
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
        
        # Validate tool name
        if not tool_name:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32602,
                    'message': 'Missing tool name'
                }
            }
        
        app = None
        capability = None
        
        # Parse tool name: mcp_identifier_app_name:capability_name or simple capability_name
        if ':' in tool_name:
            # Namespaced format: mcp_prefix_app_name:capability_name
            prefix_and_app, sanitized_cap_name = tool_name.split(':', 1)
            
            # Extract mcp_prefix and app_name from prefix_and_app
            mcp_prefix = self._sanitize_tool_name(mcp_service.identifier) if mcp_service.identifier else 'mcp'
            
            # Remove mcp_prefix from prefix_and_app to get sanitized_app_name
            if prefix_and_app.startswith(f"{mcp_prefix}_"):
                sanitized_app_name = prefix_and_app[len(mcp_prefix) + 1:]  # +1 for underscore
            else:
                # Fallback: treat entire prefix as app name (for backward compatibility)
                sanitized_app_name = prefix_and_app
            
            # Find app by matching sanitized name (apply same fallback logic as tools/list)
            all_apps = self.db.session.query(Service).filter(
                Service.mcp_service_id == mcp_service.id
            ).all()
            
            for a in all_apps:
                # Apply same sanitization and fallback logic as in tools/list
                app_sanitized_name = self._sanitize_tool_name(a.name) if a.name else 'app'
                if not app_sanitized_name or app_sanitized_name.replace('_', '').replace(':', '').replace('-', '').replace('+', '').replace('.', '') == '':
                    app_sanitized_name = 'app'
                
                if app_sanitized_name == sanitized_app_name:
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
        if capability.capability_type in ('api', 'tool'):
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
        from app.models.models import Capability
        
        # Check which capability types are actually registered for this service
        capability_types = self.db.session.query(Capability.capability_type).filter(
            Capability.app_id == service.id,
            Capability.is_enabled == True
        ).distinct().all()
        
        has_tools = False
        has_resources = False
        has_prompts = False
        
        for (cap_type,) in capability_types:
            if cap_type in ['tool', 'mcp_tool']:
                has_tools = True
            elif cap_type == 'resource':
                has_resources = True
            elif cap_type == 'prompt':
                has_prompts = True
        
        # Build capabilities dynamically based on what's registered
        capabilities = {}
        if has_tools:
            capabilities['tools'] = {}
        if has_resources:
            capabilities['resources'] = {}
        if has_prompts:
            capabilities['prompts'] = {}
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': capabilities,
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
        
        # Get all tool-type capabilities for this service (exclude resource and prompt types)
        all_capabilities = self.db.session.query(Capability).filter(
            Capability.app_id == service.id,
            Capability.capability_type.in_(['tool', 'mcp_tool']),
            Capability.is_enabled == True
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
                            # Send full schema to LLM (including const-constrained fixed params)
                            # const制約により、LLMはパラメータを認識するが値は変更できない
                            tool['inputSchema'] = {k: v for k, v in body_params.items()}
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
    
    def _handle_resources_list_for_mcp_service(self, account, mcp_service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request - return resource-type capabilities from MCP service"""
        from app.models.models import Capability, Service
        
        # Check hierarchical access at MCP service level
        if not self._check_hierarchical_access(account, mcp_service):
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'result': {
                    'resources': []  # Return empty if no access to MCP service
                }
            }
        
        # Get all apps under this MCP service
        apps = self.db.session.query(Service).filter(
            Service.mcp_service_id == mcp_service.id,
            Service.is_enabled == True
        ).all()
        
        # Aggregate resource-type capabilities from all apps
        resource_list = []
        for app in apps:
            # Check app-level access
            if not self._check_hierarchical_access(account, mcp_service, app=app):
                continue
            
            # Get all resource-type capabilities for this app
            capabilities = self.db.session.query(Capability).filter(
                Capability.app_id == app.id,
                Capability.capability_type == 'resource',
                Capability.is_enabled == True
            ).all()
            
            for resource in capabilities:
                # Check capability-level access
                if not self._check_hierarchical_access(account, mcp_service, app=app, capability=resource):
                    continue
                
                # Get identifier from the MCP service
                identifier = mcp_service.identifier
                resource_item = {
                    'uri': resource.resource_uri or f'resource://{identifier}/{resource.name}',
                    'name': resource.name,
                    'description': resource.description or ''
                }
                if resource.resource_mime_type:
                    resource_item['mimeType'] = resource.resource_mime_type
                resource_list.append(resource_item)
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'resources': resource_list
            }
        }
    
    def _handle_resources_list_for_service(self, account, service, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request - return resource-type capabilities from single service"""
        from app.models.models import Capability
        
        # Get resource-type capabilities for this service
        capabilities = self.db.session.query(Capability).filter(
            Capability.app_id == service.id,
            Capability.capability_type == 'resource',
            Capability.is_enabled == True
        ).all()
        
        account_id = account.id if account else None
        
        # Filter by access control
        resource_list = []
        for resource in capabilities:
            # Check access control
            if resource.access_control == 'restricted':
                if not account_id:
                    continue
                has_access = any(
                    caa.account_id == account_id 
                    for caa in resource.capability_account_access
                )
                if not has_access:
                    continue
            
            # Get identifier from the service's MCP service
            identifier = service.mcp_service.identifier if service.mcp_service else 'default'
            resource_item = {
                'uri': resource.resource_uri or f'resource://{identifier}/{resource.name}',
                'name': resource.name,
                'description': resource.description or ''
            }
            if resource.resource_mime_type:
                resource_item['mimeType'] = resource.resource_mime_type
            resource_list.append(resource_item)
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'resources': resource_list
            }
        }
    
    def _handle_resources_read(self, account, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request - return content for capability resource"""
        from app.models.models import Capability, Service
        
        params = mcp_request.get('params', {})
        uri = params.get('uri', '')
        
        if not uri:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32602,
                    'message': 'Missing required parameter: uri'
                }
            }
        
        account_id = account.id if account else None
        
        # Get capability resources
        resources = self.db.session.query(Capability).join(Service).filter(
            Capability.capability_type == 'resource',
            Capability.is_enabled == True,
            Service.is_enabled == True
        ).all()
        
        target_resource = None
        for resource in resources:
            identifier = resource.service.mcp_service.identifier if resource.service.mcp_service else 'default'
            stored_uri = resource.resource_uri or f'resource://{identifier}/{resource.name}'
            if stored_uri == uri or resource.name == uri:
                target_resource = resource
                break
        
        if not target_resource:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32602,
                    'message': f'Resource not found: {uri}'
                }
            }
        
        # Check access control for capability resource
        if target_resource.access_control == 'restricted':
            if not account_id:
                return {
                    'jsonrpc': '2.0',
                    'id': mcp_request.get('id') or 0,
                    'error': {
                        'code': -32600,
                        'message': 'Access denied to this resource'
                    }
                }
            
            has_access = any(
                caa.account_id == account_id 
                for caa in target_resource.capability_account_access
            )
            if not has_access:
                return {
                    'jsonrpc': '2.0',
                    'id': mcp_request.get('id') or 0,
                    'error': {
                        'code': -32600,
                        'message': 'Access denied to this resource'
                    }
                }
        
        # Return the capability resource content
        content = target_resource.template_content or ''
        mime_type = target_resource.resource_mime_type or 'text/plain'
        identifier = target_resource.service.mcp_service.identifier if target_resource.service.mcp_service else 'default'
        resource_uri = target_resource.resource_uri or f'resource://{identifier}/{target_resource.name}'
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'contents': [
                    {
                        'uri': resource_uri,
                        'mimeType': mime_type,
                        'text': content
                    }
                ]
            }
        }
    
    def _handle_prompts_list(self, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request - return all prompt-type capabilities"""
        from app.models.models import Capability, Service
        
        # Get all prompt-type capabilities across all services
        prompts = self.db.session.query(Capability).join(Service).filter(
            Capability.capability_type == 'prompt',
            Capability.is_enabled == True,
            Service.is_enabled == True
        ).all()
        
        prompt_list = []
        for prompt in prompts:
            prompt_item = {
                'name': prompt.name,
                'description': prompt.description or ''
            }
            
            # Extract arguments from body_params if exists
            if prompt.body_params:
                try:
                    body_params = json.loads(prompt.body_params) if isinstance(prompt.body_params, str) else prompt.body_params
                    if 'properties' in body_params:
                        arguments = []
                        for arg_name, arg_spec in body_params['properties'].items():
                            argument = {
                                'name': arg_name,
                                'description': arg_spec.get('description', ''),
                                'required': arg_name in body_params.get('required', [])
                            }
                            arguments.append(argument)
                        
                        if arguments:
                            prompt_item['arguments'] = arguments
                except:
                    pass
            
            prompt_list.append(prompt_item)
        
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'prompts': prompt_list
            }
        }
    
    def _handle_prompts_get(self, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request - return specific prompt with filled template"""
        from app.models.models import Capability, Resource
        
        params = mcp_request.get('params', {})
        prompt_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if not prompt_name:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32602,
                    'message': 'Missing prompt name'
                }
            }
        
        # Find prompt capability
        prompt = self.db.session.query(Capability).filter(
            Capability.name == prompt_name,
            Capability.capability_type == 'prompt',
            Capability.is_enabled == True
        ).first()
        
        if not prompt:
            return {
                'jsonrpc': '2.0',
                'id': mcp_request.get('id') or 0,
                'error': {
                    'code': -32602,
                    'message': f'Prompt not found: {prompt_name}'
                }
            }
        
        # Get template content from either template_content field or global Resource
        template = ''
        if prompt.template_content:
            template = prompt.template_content
        elif prompt.global_resource_id:
            # Get template from Resource table
            resource = self.db.session.query(Resource).filter(
                Resource.id == prompt.global_resource_id,
                Resource.is_enabled == True
            ).first()
            if resource:
                template = resource.content or ''
        
        # Simple variable replacement: {{variable_name}}
        for key, value in arguments.items():
            template = template.replace(f'{{{{{key}}}}}', str(value))
        
        # Return formatted prompt
        return {
            'jsonrpc': '2.0',
            'id': mcp_request.get('id') or 0,
            'result': {
                'description': prompt.description or '',
                'messages': [
                    {
                        'role': 'user',
                        'content': {
                            'type': 'text',
                            'text': template
                        }
                    }
                ]
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
        
        # Build final request body
        body = {}
        
        if capability.body_params:
            # body_params can be string (JSON) or dict
            body_params = capability.body_params
            if isinstance(body_params, str):
                # JSON string: parse it
                try:
                    parsed = json.loads(body_params)
                    
                    # Check if it's JSON Schema format with properties
                    if 'properties' in parsed:
                        # Extract const-constrained fixed params from schema
                        properties = parsed.get('properties', {})
                        
                        # First, add const values (fixed params)
                        for key, prop_def in properties.items():
                            if 'const' in prop_def:
                                # This is a fixed parameter with const constraint
                                const_value = prop_def['const']
                                # Replace variables in const value
                                if isinstance(const_value, str):
                                    body[key] = VariableReplacer.replace_in_string(const_value)
                                else:
                                    body[key] = const_value
                        
                        # Then, merge LLM-provided arguments (override if not const)
                        for key, value in arguments.items():
                            if key in properties and 'const' not in properties[key]:
                                # This is an LLM parameter (no const constraint)
                                body[key] = value
                            elif key not in properties:
                                # Unknown parameter from LLM (allow it)
                                body[key] = value
                            # If key has const constraint, ignore LLM value (already set above)
                    else:
                        # Old format: simple key-value, treat as fixed params
                        body.update(VariableReplacer.replace_in_dict(parsed))
                        body.update(arguments)
                except (json.JSONDecodeError, TypeError):
                    pass
            else:
                # Dict: should not happen, but handle it
                try:
                    parsed = json.loads(body_params)
                    if 'properties' in parsed:
                        # Same logic as above
                        properties = parsed.get('properties', {})
                        for key, prop_def in properties.items():
                            if 'const' in prop_def:
                                const_value = prop_def['const']
                                if isinstance(const_value, str):
                                    body[key] = VariableReplacer.replace_in_string(const_value)
                                else:
                                    body[key] = const_value
                        for key, value in arguments.items():
                            if key in properties and 'const' not in properties[key]:
                                body[key] = value
                            elif key not in properties:
                                body[key] = value
                    else:
                        body.update(VariableReplacer.replace_in_dict(parsed))
                        body.update(arguments)
                except (json.JSONDecodeError, TypeError):
                    pass
        else:
            # No body_params defined, use LLM arguments directly
            body.update(arguments)
        
        # Check HTTP method from headers
        http_method = headers.get('X-HTTP-Method', 'POST').upper()
        
        # Get timeout from capability settings
        timeout_seconds = float(capability.timeout_seconds or 30)
        
        try:
            # Make HTTP request
            if http_method == 'GET':
                # For GET, use query parameters instead of body
                response = httpx.get(
                    url,
                    params=body,  # Query parameters
                    headers=headers,
                    timeout=timeout_seconds
                )
            else:
                # POST or other methods
                response = httpx.post(
                    url,
                    headers=headers,
                    json=body,
                    timeout=timeout_seconds
                )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except httpx.TimeoutException as e:
            return {
                'success': False,
                'error': {
                    'code': 'API_TIMEOUT',
                    'message': f'APIリクエストがタイムアウトしました（{timeout_seconds}秒）',
                    'details': {
                        'url': url,
                        'timeout': timeout_seconds,
                        'suggestion': 'Capability設定でtimeout_secondsを増やすか、API側の負荷を確認してください'
                    }
                }
            }
        except httpx.HTTPStatusError as e:
            return {
                'success': False,
                'error': {
                    'code': f'HTTP_{e.response.status_code}',
                    'message': f'HTTPエラー: {e.response.status_code} {e.response.reason_phrase}',
                    'details': {
                        'url': url,
                        'status_code': e.response.status_code,
                        'response_body': e.response.text[:500] if e.response.text else None
                    }
                }
            }
        except httpx.HTTPError as e:
            return {
                'success': False,
                'error': {
                    'code': 'HTTP_ERROR',
                    'message': f'HTTP通信エラー: {str(e)}',
                    'details': {
                        'url': url,
                        'error_type': type(e).__name__
                    }
                }
            }
    
    def _execute_mcp_call(self, service, capability, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP relay call"""
        # For MCP relay, we need to connect to another MCP server
        
        try:
            # Parse MCP server URL
            # For mcp_tool type, use service.mcp_url (capability.service is the Service/App model)
            app = capability.service
            mcp_transport = getattr(app, 'mcp_transport', 'http') or 'http'
            mcp_url = app.mcp_url if app else capability.url
            
            # Check if stdio transport
            if mcp_transport == 'stdio':
                return self._execute_stdio_mcp_call(app, capability, arguments)
            
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
                    
                    # Get timeout from capability settings
                    timeout_seconds = float(capability.timeout_seconds or 30)
                    
                    logger.debug(f"Initializing MCP session at {mcp_url}")
                    init_response = httpx.post(
                        mcp_url,
                        headers=headers,
                        json=init_request,
                        timeout=timeout_seconds
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
                    timeout=timeout_seconds
                )
                
                logger.debug(f"MCP response status: {response.status_code}, body: {response.text}")
                response.raise_for_status()
                
                return response.json()
            
            else:
                return {
                    'success': False,
                    'error': 'Unsupported MCP transport'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_stdio_mcp_call(self, app, capability, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute stdio MCP relay call"""
        try:
            # Get stdio configuration from app
            command = app.stdio_command
            args = json.loads(app.stdio_args) if app.stdio_args else []
            env = json.loads(app.stdio_env) if app.stdio_env else {}
            cwd = app.stdio_cwd
            
            if not command:
                return {
                    'success': False,
                    'error': 'stdio command is not configured'
                }
            
            # Replace variables in args and env
            from app.services.variable_replacer import VariableReplacer
            replacer = VariableReplacer()
            
            # Replace variables in args
            resolved_args = [replacer.replace_in_string(str(arg)) for arg in args]
            
            # Replace variables in env
            resolved_env = {}
            for key, value in env.items():
                resolved_env[key] = replacer.replace_in_string(str(value))
            
            # Run the async call
            result = asyncio.run(self._async_stdio_mcp_call(
                command, resolved_args, resolved_env, cwd,
                capability.name, arguments
            ))
            
            return result
        
        except Exception as e:
            logger.error(f"stdio MCP call failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _async_stdio_mcp_call(
        self, 
        command: str, 
        args: List[str], 
        env: Dict[str, str], 
        cwd: Optional[str],
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Async implementation of stdio MCP call"""
        import os
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env={**os.environ, **env} if env else None,
            cwd=cwd
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    
                    # Call the tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Convert result to dict format
                    if result.content:
                        content_list = []
                        for item in result.content:
                            if hasattr(item, 'text'):
                                content_list.append({
                                    'type': 'text',
                                    'text': item.text
                                })
                            elif hasattr(item, 'data'):
                                content_list.append({
                                    'type': 'blob',
                                    'data': item.data
                                })
                            else:
                                content_list.append({
                                    'type': 'unknown',
                                    'value': str(item)
                                })
                        
                        return {
                            'jsonrpc': '2.0',
                            'id': 1,
                            'result': {
                                'content': content_list,
                                'isError': result.isError if hasattr(result, 'isError') else False
                            }
                        }
                    else:
                        return {
                            'jsonrpc': '2.0',
                            'id': 1,
                            'result': {
                                'content': [],
                                'isError': False
                            }
                        }
        
        except Exception as e:
            logger.error(f"async stdio MCP call error: {e}")
            return {
                'jsonrpc': '2.0',
                'id': 1,
                'error': {
                    'code': -32603,
                    'message': str(e)
                }
            }


def execute_capability_api(capability, params: Dict[str, Any] = None):
    """
    Execute a capability API call for testing purposes
    
    Args:
        capability: Capability model instance
        params: Dictionary of parameters to pass to the API
    
    Returns:
        Dictionary with execution results including success status, data, and execution time
    """
    import time
    from app.services.variable_replacer import VariableReplacer
    
    start_time = time.time()
    params = params or {}
    
    # Handle Resource type: simply return the stored content
    if capability.capability_type == 'resource':
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        resource_content = capability.template_content or ''
        resource_uri = capability.resource_uri or ''
        resource_mime_type = capability.resource_mime_type or 'text/plain'
        
        return {
            'success': True,
            'status_code': 200,
            'data': {
                'uri': resource_uri,
                'mimeType': resource_mime_type,
                'text': resource_content
            },
            'execution_time_ms': execution_time_ms
        }
    
    # Get the service (app) from capability
    service = capability.service
    
    # Merge headers: service common headers + capability specific headers
    headers = {}
    if service.common_headers:
        headers.update(json.loads(service.common_headers))
    if capability.headers:
        headers.update(json.loads(capability.headers))
    
    # Replace variables in headers
    headers = VariableReplacer.replace_in_dict(headers)
    
    # Replace variables in URL
    url = VariableReplacer.replace_in_string(capability.url)
    
    # Build final request body
    body = {}
    
    if capability.body_params:
        try:
            parsed = json.loads(capability.body_params) if isinstance(capability.body_params, str) else capability.body_params
            
            if 'properties' in parsed:
                # Extract const-constrained fixed params from schema
                properties = parsed.get('properties', {})
                
                # Add const values (fixed params)
                for key, prop_def in properties.items():
                    if 'const' in prop_def:
                        const_value = prop_def['const']
                        if isinstance(const_value, str):
                            body[key] = VariableReplacer.replace_in_string(const_value)
                        else:
                            body[key] = const_value
                
                # Merge user-provided parameters
                for key, value in params.items():
                    if key in properties and 'const' not in properties[key]:
                        body[key] = value
                    elif key not in properties:
                        body[key] = value
            else:
                # Simple key-value format
                body.update(VariableReplacer.replace_in_dict(parsed))
                body.update(params)
        except (json.JSONDecodeError, TypeError):
            body.update(params)
    else:
        body.update(params)
    
    # Get HTTP method
    http_method = headers.get('X-HTTP-Method', 'POST').upper()
    
    # Get timeout from capability settings
    timeout_seconds = float(capability.timeout_seconds or 30)
    
    try:
        # Make HTTP request
        if http_method == 'GET':
            response = httpx.get(
                url,
                params=body,
                headers=headers,
                timeout=timeout_seconds
            )
        else:
            response = httpx.post(
                url,
                headers=headers,
                json=body,
                timeout=timeout_seconds
            )
        
        response.raise_for_status()
        
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        return {
            'success': True,
            'status_code': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'execution_time_ms': execution_time_ms
        }
    except httpx.TimeoutException as e:
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        return {
            'success': False,
            'error': {
                'code': 'API_TIMEOUT',
                'message': f'APIリクエストがタイムアウトしました（{timeout_seconds}秒）',
                'details': {
                    'url': url,
                    'timeout': timeout_seconds,
                    'suggestion': 'Capability設定でtimeout_secondsを増やすか、API側の負荷を確認してください'
                }
            },
            'execution_time_ms': execution_time_ms
        }
    except httpx.HTTPStatusError as e:
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        return {
            'success': False,
            'error': {
                'code': f'HTTP_{e.response.status_code}',
                'message': f'HTTPエラー: {e.response.status_code} {e.response.reason_phrase}',
                'details': {
                    'url': url,
                    'status_code': e.response.status_code,
                    'response_body': e.response.text[:500] if e.response.text else None
                }
            },
            'execution_time_ms': execution_time_ms
        }
    except httpx.HTTPError as e:
        end_time = time.time()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        return {
            'success': False,
            'error': {
                'code': 'HTTP_ERROR',
                'message': f'HTTP通信エラー: {str(e)}',
                'details': {
                    'url': url,
                    'error_type': type(e).__name__
                }
            },
            'execution_time_ms': execution_time_ms
        }
