"""
MCP Controller
Handles MCP protocol endpoints
"""
import json
import logging
from flask import Blueprint, request, jsonify, current_app, Response

from app.models.models import ConnectionAccount, Service, McpService, Capability
from app.services.mcp_handler import MCPHandler
from app.services.mcp_logger import LogContext, create_log_context_from_request, log_mcp_request
from app.models.models import db

mcp_bp = Blueprint('mcp', __name__)
logger = logging.getLogger(__name__)

# Initialize MCP handler
mcp_handler = MCPHandler(db)


def get_subdomain_from_request():
    """Extract subdomain from request host"""
    host = request.host.split(':')[0]  # Remove port if present
    
    # Handle lvh.me domain (subdomain.lvh.me)
    if '.lvh.me' in host:
        subdomain = host.replace('.lvh.me', '')
        logger.debug(f"Extracted subdomain from lvh.me: {subdomain}")
        return subdomain if subdomain else None
    
    # Handle localhost with subdomain parameter
    subdomain = request.args.get('subdomain') or request.headers.get('X-Subdomain')
    logger.debug(f"Extracted subdomain from param/header: {subdomain}")
    return subdomain


def authenticate_bearer_token():
    """Authenticate connection account from Bearer token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        logger.warning("Missing or invalid Authorization header")
        return None, {'error': 'Missing or invalid Authorization header'}, 401
    
    bearer_token = auth_header[7:]  # Remove 'Bearer ' prefix
    account = ConnectionAccount.query.filter_by(bearer_token=bearer_token).first()
    
    if not account:
        logger.warning(f"Invalid bearer token: {bearer_token[:10]}...")
        return None, {'error': 'Invalid bearer token'}, 401
    
    logger.debug(f"Authenticated account: {account.name}")
    return account, None, None


@mcp_bp.route('/mcp', methods=['POST', 'GET'])
def mcp_subdomain_endpoint():
    """
    MCP endpoint with subdomain routing
    Access: <subdomain>.lvh.me/mcp or localhost:5000/mcp?subdomain=<subdomain>
    
    Handles:
    - GET: Returns capabilities list for the service
    - POST: Processes MCP tool calls
    """
    logger.info(f"MCP request: {request.method} {request.url}")
    
    # Initialize log context
    log_context = create_log_context_from_request(request)
    
    # Get request ID if available
    request_id = None
    mcp_request = None
    if request.method == 'POST':
        try:
            mcp_request = request.get_json()
            if mcp_request:
                request_id = mcp_request.get('id')
                log_context.request_id = str(request_id) if request_id else None
                log_context.mcp_method = mcp_request.get('method', 'unknown')
                log_context.request_body = json.dumps(mcp_request, ensure_ascii=False)
                
                # Extract tool name for tools/call
                if log_context.mcp_method == 'tools/call':
                    params = mcp_request.get('params', {})
                    log_context.tool_name = params.get('name')
        except:
            pass
    else:
        log_context.mcp_method = 'GET'
    
    # Extract subdomain
    subdomain = get_subdomain_from_request()
    if not subdomain:
        logger.warning("Subdomain not specified in request")
        error_response = {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32600,
                'message': 'Subdomain not specified. Use <subdomain>.lvh.me/mcp or add ?subdomain=<subdomain>'
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=400,
            is_success=False,
            error_code=-32600,
            error_message='Subdomain not specified'
        )
        return jsonify(error_response), 400
    
    logger.debug(f"Processing request for subdomain: {subdomain}")
    
    # Get MCP service by subdomain
    mcp_service = McpService.query.filter_by(identifier=subdomain).first()
    if not mcp_service:
        error_response = {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32001,
                'message': f'MCP service not found for subdomain: {subdomain}'
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=404,
            is_success=False,
            error_code=-32001,
            error_message=f'MCP service not found for subdomain: {subdomain}'
        )
        return jsonify(error_response), 404
    
    # Set MCP service info in log context
    log_context.mcp_service_id = mcp_service.id
    log_context.mcp_service_name = mcp_service.name
    log_context.access_control = mcp_service.access_control
    
    # Authenticate account - only required if access_control is 'restricted'
    account = None
    if mcp_service.access_control == 'restricted':
        account, error, status = authenticate_bearer_token()
        if error:
            logger.error(f"Authentication failed for subdomain {subdomain}")
            error_response = {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32000,
                    'message': error['error']
                }
            }
            log_mcp_request(
                current_app._get_current_object(),
                log_context,
                response_body=json.dumps(error_response, ensure_ascii=False),
                status_code=status,
                is_success=False,
                error_code=-32000,
                error_message=error['error']
            )
            return jsonify(error_response), status
        
        # Set account info in log context
        log_context.account_id = account.id
        log_context.account_name = account.name
    
    # Get apps (services) under this MCP service
    services = Service.query.filter_by(mcp_service_id=mcp_service.id).all()
    
    # Handle GET request - return capabilities from all services
    if request.method == 'GET':
        all_capabilities = []
        for service in services:
            capabilities = Capability.query.filter_by(app_id=service.id).all()
            all_capabilities.extend([cap.to_dict() for cap in capabilities])
        
        response = {
            'jsonrpc': '2.0',
            'result': {
                'capabilities': all_capabilities,
                'serverInfo': {
                    'name': mcp_service.name,
                    'version': '1.0.0'
                }
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(response, ensure_ascii=False),
            status_code=200,
            is_success=True
        )
        return jsonify(response)
    
    # Handle POST request - process MCP request
    if not mcp_request:
        error_response = {
            'jsonrpc': '2.0',
            'id': 0,
            'error': {
                'code': -32700,
                'message': 'Parse error: Invalid JSON'
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=400,
            is_success=False,
            error_code=-32700,
            error_message='Parse error: Invalid JSON'
        )
        return jsonify(error_response), 400
    
    # Check if this is a notification (no id field or method starts with 'notifications/')
    is_notification = 'id' not in mcp_request or mcp_request.get('method', '').startswith('notifications/')
    
    if is_notification:
        # Process notification but don't return a response
        logger.info(f"Received notification: {mcp_request.get('method')}")
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            status_code=202,
            is_success=True
        )
        # For notifications, return 204 No Content
        return Response('', status=202, mimetype='application/json')
    
    # Route to MCP handler - pass mcp_service for multi-service handling
    response = mcp_handler.handle_mcp_service_request(account, mcp_service, mcp_request)
    
    # Determine if response is success or error
    is_success = 'error' not in response
    error_code = response.get('error', {}).get('code') if not is_success else None
    error_message = response.get('error', {}).get('message') if not is_success else None
    
    log_mcp_request(
        current_app._get_current_object(),
        log_context,
        response_body=json.dumps(response, ensure_ascii=False),
        status_code=200 if is_success else 400,
        is_success=is_success,
        error_code=error_code,
        error_message=error_message
    )
    
    return jsonify(response)


@mcp_bp.route('/<path_identifier>/mcp', methods=['POST', 'GET'])
def mcp_path_endpoint(path_identifier):
    """
    Path-based MCP endpoint
    Access: http://localhost:5100/<path_identifier>/mcp
    
    Handles:
    - GET: Returns capabilities list for the service
    - POST: Processes MCP tool calls
    """
    logger.info(f"MCP path-based request: {request.method} {request.url}")
    logger.debug(f"Path identifier: {path_identifier}")
    
    # Initialize log context
    log_context = create_log_context_from_request(request)
    
    # Get request ID if available
    request_id = None
    mcp_request = None
    if request.method == 'POST':
        try:
            mcp_request = request.get_json()
            if mcp_request:
                request_id = mcp_request.get('id')
                log_context.request_id = str(request_id) if request_id else None
                log_context.mcp_method = mcp_request.get('method', 'unknown')
                log_context.request_body = json.dumps(mcp_request, ensure_ascii=False)
                
                # Extract tool name for tools/call
                if log_context.mcp_method == 'tools/call':
                    params = mcp_request.get('params', {})
                    log_context.tool_name = params.get('name')
        except:
            pass
    else:
        log_context.mcp_method = 'GET'
    
    # Get MCP service by subdomain with routing_type='path'
    mcp_service = McpService.query.filter_by(
        identifier=path_identifier,
        routing_type='path'
    ).first()
    
    if not mcp_service:
        error_response = {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32001,
                'message': f'MCP service not found for path: {path_identifier}'
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=404,
            is_success=False,
            error_code=-32001,
            error_message=f'MCP service not found for path: {path_identifier}'
        )
        return jsonify(error_response), 404
    
    # Set MCP service info in log context
    log_context.mcp_service_id = mcp_service.id
    log_context.mcp_service_name = mcp_service.name
    log_context.access_control = mcp_service.access_control
    
    # Authenticate account - only required if access_control is 'restricted'
    account = None
    if mcp_service.access_control == 'restricted':
        account, error, status = authenticate_bearer_token()
        if error:
            logger.error(f"Authentication failed for path {path_identifier}")
            error_response = {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32000,
                    'message': error['error']
                }
            }
            log_mcp_request(
                current_app._get_current_object(),
                log_context,
                response_body=json.dumps(error_response, ensure_ascii=False),
                status_code=status,
                is_success=False,
                error_code=-32000,
                error_message=error['error']
            )
            return jsonify(error_response), status
        
        # Set account info in log context
        log_context.account_id = account.id
        log_context.account_name = account.name
    
    # Get apps (services) under this MCP service
    services = Service.query.filter_by(mcp_service_id=mcp_service.id).all()
    
    # Handle GET request - return capabilities from all services
    if request.method == 'GET':
        all_capabilities = []
        for service in services:
            capabilities = Capability.query.filter_by(app_id=service.id).all()
            all_capabilities.extend([cap.to_dict() for cap in capabilities])
        
        response = {
            'jsonrpc': '2.0',
            'result': {
                'capabilities': all_capabilities,
                'serverInfo': {
                    'name': mcp_service.name,
                    'version': '1.0.0'
                }
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(response, ensure_ascii=False),
            status_code=200,
            is_success=True
        )
        return jsonify(response)
    
    # Handle POST request - process MCP request
    if not mcp_request:
        error_response = {
            'jsonrpc': '2.0',
            'id': 0,
            'error': {
                'code': -32700,
                'message': 'Parse error: Invalid JSON'
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=400,
            is_success=False,
            error_code=-32700,
            error_message='Parse error: Invalid JSON'
        )
        return jsonify(error_response), 400
    
    # Check if this is a notification (no id field or method starts with 'notifications/')
    is_notification = 'id' not in mcp_request or mcp_request.get('method', '').startswith('notifications/')
    
    if is_notification:
        # Process notification but don't return a response
        logger.info(f"Received notification: {mcp_request.get('method')}")
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            status_code=202,
            is_success=True
        )
        # For notifications, return 204 No Content
        return Response('', status=202, mimetype='application/json')
    
    # Route to MCP handler - pass mcp_service for multi-service handling
    response = mcp_handler.handle_mcp_service_request(account, mcp_service, mcp_request)
    
    # Determine if response is success or error
    is_success = 'error' not in response
    error_code = response.get('error', {}).get('code') if not is_success else None
    error_message = response.get('error', {}).get('message') if not is_success else None
    
    log_mcp_request(
        current_app._get_current_object(),
        log_context,
        response_body=json.dumps(response, ensure_ascii=False),
        status_code=200 if is_success else 400,
        is_success=is_success,
        error_code=error_code,
        error_message=error_message
    )
    
    return jsonify(response)


@mcp_bp.route('/tools/<tool_id>', methods=['POST'])
def mcp_tool_endpoint(tool_id):
    """
    Direct tool execution endpoint
    Access: <subdomain>.lvh.me/tools/<tool_id>
    
    Executes a specific tool/capability directly
    """
    # Initialize log context
    log_context = create_log_context_from_request(request)
    log_context.mcp_method = 'tools/call'
    log_context.tool_name = tool_id
    
    # Extract subdomain
    subdomain = get_subdomain_from_request()
    if not subdomain:
        error_response = {
            'jsonrpc': '2.0',
            'error': {
                'code': -32600,
                'message': 'Subdomain not specified'
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=400,
            is_success=False,
            error_code=-32600,
            error_message='Subdomain not specified'
        )
        return jsonify(error_response), 400
    
    # Authenticate account
    account, error, status = authenticate_bearer_token()
    if error:
        error_response = {
            'jsonrpc': '2.0',
            'error': {
                'code': -32000,
                'message': error['error']
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=status,
            is_success=False,
            error_code=-32000,
            error_message=error['error']
        )
        return jsonify(error_response), status
    
    # Set account info in log context
    log_context.account_id = account.id
    log_context.account_name = account.name
    log_context.access_control = 'restricted'
    
    # Get service by subdomain
    service = Service.query.filter_by(subdomain=subdomain).first()
    if not service:
        error_response = {
            'jsonrpc': '2.0',
            'error': {
                'code': -32001,
                'message': f'Service not found for subdomain: {subdomain}'
            }
        }
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=404,
            is_success=False,
            error_code=-32001,
            error_message=f'Service not found for subdomain: {subdomain}'
        )
        return jsonify(error_response), 404
    
    # Set app info in log context
    log_context.app_id = service.id
    log_context.app_name = service.name
    if service.mcp_service:
        log_context.mcp_service_id = service.mcp_service.id
        log_context.mcp_service_name = service.mcp_service.name
    
    # Get tool arguments from request
    data = request.get_json() or {}
    arguments = data.get('arguments', {})
    log_context.request_body = json.dumps(data, ensure_ascii=False)
    
    # Execute tool
    response = mcp_handler.execute_tool_by_id(account, service, tool_id, arguments)
    
    # Determine if response is success or error
    is_success = 'error' not in response
    error_code = response.get('error', {}).get('code') if not is_success else None
    error_message = response.get('error', {}).get('message') if not is_success else None
    
    log_mcp_request(
        current_app._get_current_object(),
        log_context,
        response_body=json.dumps(response, ensure_ascii=False),
        status_code=200 if is_success else 400,
        is_success=is_success,
        error_code=error_code,
        error_message=error_message
    )
    
    return jsonify(response)


@mcp_bp.route('/mcp/<subdomain>', methods=['POST'])
def mcp_http_endpoint(subdomain):
    """
    Legacy HTTP MCP endpoint (backward compatibility)
    Access: /mcp/<subdomain>
    """
    # Initialize log context
    log_context = create_log_context_from_request(request)
    log_context.mcp_method = 'legacy_http'
    
    # Authenticate account
    account, error, status = authenticate_bearer_token()
    if error:
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error, ensure_ascii=False),
            status_code=status,
            is_success=False,
            error_message=error.get('error')
        )
        return jsonify(error), status
    
    # Set account info in log context
    log_context.account_id = account.id
    log_context.account_name = account.name
    log_context.access_control = 'restricted'
    
    # Get service by subdomain
    service = Service.query.filter_by(subdomain=subdomain).first()
    if not service:
        error_response = {'error': 'Service not found'}
        log_mcp_request(
            current_app._get_current_object(),
            log_context,
            response_body=json.dumps(error_response, ensure_ascii=False),
            status_code=404,
            is_success=False,
            error_message='Service not found'
        )
        return jsonify(error_response), 404
    
    # Set app info in log context
    log_context.app_id = service.id
    log_context.app_name = service.name
    if service.mcp_service:
        log_context.mcp_service_id = service.mcp_service.id
        log_context.mcp_service_name = service.mcp_service.name
    
    # Handle MCP request
    mcp_request = request.get_json()
    log_context.request_body = json.dumps(mcp_request, ensure_ascii=False) if mcp_request else None
    
    response = mcp_handler.handle_http_request(account, service, mcp_request)
    
    # Determine if response is success or error
    is_success = 'error' not in response
    error_message = response.get('error') if not is_success else None
    
    log_mcp_request(
        current_app._get_current_object(),
        log_context,
        response_body=json.dumps(response, ensure_ascii=False),
        status_code=200 if is_success else 400,
        is_success=is_success,
        error_message=error_message
    )
    
    return jsonify(response)
