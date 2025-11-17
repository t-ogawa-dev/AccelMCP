"""
MCP Controller
Handles MCP protocol endpoints
"""
from flask import Blueprint, request, jsonify

from app.models.models import ConnectionAccount, Service
from app.services.mcp_handler import MCPHandler
from app.models.models import db

mcp_bp = Blueprint('mcp', __name__)

# Initialize MCP handler
mcp_handler = MCPHandler(db)


def get_subdomain_from_request():
    """Extract subdomain from request host"""
    host = request.host.split(':')[0]  # Remove port if present
    
    # Handle lvh.me domain (subdomain.lvh.me)
    if '.lvh.me' in host:
        subdomain = host.replace('.lvh.me', '')
        return subdomain if subdomain else None
    
    # Handle localhost with subdomain parameter
    return request.args.get('subdomain') or request.headers.get('X-Subdomain')


def authenticate_bearer_token():
    """Authenticate connection account from Bearer token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, {'error': 'Missing or invalid Authorization header'}, 401
    
    bearer_token = auth_header[7:]  # Remove 'Bearer ' prefix
    account = ConnectionAccount.query.filter_by(bearer_token=bearer_token).first()
    
    if not account:
        return None, {'error': 'Invalid bearer token'}, 401
    
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
    # Extract subdomain
    subdomain = get_subdomain_from_request()
    if not subdomain:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32600,
                'message': 'Subdomain not specified. Use <subdomain>.lvh.me/mcp or add ?subdomain=<subdomain>'
            }
        }), 400
    
    # Authenticate account
    account, error, status = authenticate_bearer_token()
    if error:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32000,
                'message': error['error']
            }
        }), status
    
    # Get service by subdomain
    service = Service.query.filter_by(subdomain=subdomain).first()
    if not service:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32001,
                'message': f'Service not found for subdomain: {subdomain}'
            }
        }), 404
    
    # Handle GET request - return capabilities
    if request.method == 'GET':
        response = mcp_handler.get_capabilities(account, service)
        return jsonify(response)
    
    # Handle POST request - process MCP request
    mcp_request = request.get_json()
    if not mcp_request:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32700,
                'message': 'Parse error: Invalid JSON'
            }
        }), 400
    
    response = mcp_handler.handle_http_request(account, service, mcp_request)
    return jsonify(response)


@mcp_bp.route('/tools/<tool_id>', methods=['POST'])
def mcp_tool_endpoint(tool_id):
    """
    Direct tool execution endpoint
    Access: <subdomain>.lvh.me/tools/<tool_id>
    
    Executes a specific tool/capability directly
    """
    # Extract subdomain
    subdomain = get_subdomain_from_request()
    if not subdomain:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32600,
                'message': 'Subdomain not specified'
            }
        }), 400
    
    # Authenticate account
    account, error, status = authenticate_bearer_token()
    if error:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32000,
                'message': error['error']
            }
        }), status
    
    # Get service by subdomain
    service = Service.query.filter_by(subdomain=subdomain).first()
    if not service:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32001,
                'message': f'Service not found for subdomain: {subdomain}'
            }
        }), 404
    
    # Get tool arguments from request
    data = request.get_json() or {}
    arguments = data.get('arguments', {})
    
    # Execute tool
    response = mcp_handler.execute_tool_by_id(account, service, tool_id, arguments)
    return jsonify(response)


@mcp_bp.route('/mcp/<subdomain>', methods=['POST'])
def mcp_http_endpoint(subdomain):
    """
    Legacy HTTP MCP endpoint (backward compatibility)
    Access: /mcp/<subdomain>
    """
    # Authenticate account
    account, error, status = authenticate_bearer_token()
    if error:
        return jsonify(error), status
    
    # Get service by subdomain
    service = Service.query.filter_by(subdomain=subdomain).first()
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    # Handle MCP request
    mcp_request = request.get_json()
    response = mcp_handler.handle_http_request(account, service, mcp_request)
    
    return jsonify(response)
