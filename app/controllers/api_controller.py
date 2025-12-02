"""
API Controller
Handles RESTful API endpoints for services, capabilities, accounts, and permissions
"""
import json
import secrets
from flask import Blueprint, request, jsonify
from app.controllers.auth_controller import login_required

from app.models.models import db, ConnectionAccount, McpService, Service, Capability, AccountPermission, AdminSettings, Variable

# Service is now mapped to 'apps' table, but keep the class name for compatibility

api_bp = Blueprint('api', __name__)


# ============= MCP Service API =============

@api_bp.route('/mcp-services', methods=['GET', 'POST'])
@login_required
def mcp_services():
    """Get all MCP services or create new MCP service"""
    if request.method == 'GET':
        services = McpService.query.all()
        return jsonify([s.to_dict() for s in services])
    
    elif request.method == 'POST':
        data = request.get_json()
        mcp_service = McpService(
            name=data['name'],
            subdomain=data['subdomain'],
            description=data.get('description', '')
        )
        db.session.add(mcp_service)
        db.session.commit()
        return jsonify(mcp_service.to_dict()), 201


@api_bp.route('/mcp-services/<int:mcp_service_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def mcp_service_detail(mcp_service_id):
    """Get, update, or delete a specific MCP service"""
    mcp_service = McpService.query.get_or_404(mcp_service_id)
    
    if request.method == 'GET':
        result = mcp_service.to_dict()
        # Include apps list
        result['apps'] = [app.to_dict() for app in mcp_service.apps]
        return jsonify(result)
    
    elif request.method == 'PUT':
        data = request.get_json()
        mcp_service.name = data.get('name', mcp_service.name)
        mcp_service.subdomain = data.get('subdomain', mcp_service.subdomain)
        mcp_service.description = data.get('description', mcp_service.description)
        db.session.commit()
        return jsonify(mcp_service.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(mcp_service)
        db.session.commit()
        return '', 204


@api_bp.route('/mcp-services/<int:mcp_service_id>/toggle', methods=['POST'])
@login_required
def toggle_mcp_service(mcp_service_id):
    """Toggle MCP service enabled/disabled status"""
    mcp_service = McpService.query.get_or_404(mcp_service_id)
    mcp_service.is_enabled = not mcp_service.is_enabled
    db.session.commit()
    return jsonify(mcp_service.to_dict())


@api_bp.route('/mcp-services/<int:mcp_service_id>/export', methods=['GET'])
@login_required
def export_mcp_service(mcp_service_id):
    """Export MCP service with all apps and capabilities"""
    mcp_service = McpService.query.get_or_404(mcp_service_id)
    
    # Build nested structure: service -> apps -> capabilities
    export_data = {
        'name': mcp_service.name,
        'subdomain': mcp_service.subdomain,
        'description': mcp_service.description,
        'apps': []
    }
    
    # Include all apps under this service
    for app in mcp_service.apps:
        app_data = {
            'name': app.name,
            'description': app.description,
            'service_type': app.service_type,
            'mcp_url': app.mcp_url,
            'common_headers': json.loads(app.common_headers) if app.common_headers else {},
            'capabilities': []
        }
        
        # Include all capabilities under this app
        for capability in app.capabilities:
            cap_data = {
                'name': capability.name,
                'capability_type': capability.capability_type,
                'description': capability.description,
                'url': capability.url,
                'headers': json.loads(capability.headers) if capability.headers else {},
                'body_params': json.loads(capability.body_params) if capability.body_params else {},
                'template_content': capability.template_content
            }
            app_data['capabilities'].append(cap_data)
        
        export_data['apps'].append(app_data)
    
    return jsonify(export_data)


@api_bp.route('/mcp-services/import', methods=['POST'])
@login_required
def import_mcp_service():
    """Import MCP service from exported JSON"""
    import string
    import random
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('subdomain'):
        return jsonify({'error': 'Missing required fields: name, subdomain'}), 400
    
    # Check for subdomain collision
    original_subdomain = data['subdomain']
    subdomain = original_subdomain
    
    # If subdomain exists, append random 5 characters
    while McpService.query.filter_by(subdomain=subdomain).first():
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        subdomain = f"{original_subdomain}-{random_suffix}"
    
    # Create MCP service
    mcp_service = McpService(
        name=data['name'],
        subdomain=subdomain,
        description=data.get('description', '')
    )
    db.session.add(mcp_service)
    db.session.flush()  # Get ID without committing
    
    # Import apps
    for app_data in data.get('apps', []):
        app = Service(
            mcp_service_id=mcp_service.id,
            name=app_data['name'],
            description=app_data.get('description', ''),
            service_type=app_data.get('service_type', 'api'),
            mcp_url=app_data.get('mcp_url'),
            common_headers=json.dumps(app_data.get('common_headers', {}))
        )
        db.session.add(app)
        db.session.flush()  # Get ID without committing
        
        # Import capabilities
        for cap_data in app_data.get('capabilities', []):
            capability = Capability(
                app_id=app.id,
                name=cap_data['name'],
                capability_type=cap_data.get('capability_type', 'resource'),
                description=cap_data.get('description', ''),
                url=cap_data.get('url', ''),
                headers=json.dumps(cap_data.get('headers', {})),
                body_params=json.dumps(cap_data.get('body_params', {})),
                template_content=cap_data.get('template_content')
            )
            db.session.add(capability)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'mcp_service': mcp_service.to_dict(),
        'subdomain_changed': subdomain != original_subdomain
    }), 201


# ============= App API =============

@api_bp.route('/apps/test-connection', methods=['POST'])
@login_required
def test_service_connection():
    """Test MCP server connection"""
    data = request.get_json()
    mcp_url = data.get('mcp_url')
    common_headers = data.get('common_headers', {})
    
    if not mcp_url:
        return jsonify({'success': False, 'error': 'MCP URL is required'}), 400
    
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        from app.services.variable_replacer import VariableReplacer
        
        # Replace variables in headers if any
        replacer = VariableReplacer()
        resolved_headers = {}
        unresolved_vars = []
        
        for key, value in common_headers.items():
            resolved_key = replacer.replace_in_string(key)
            resolved_value = replacer.replace_in_string(value)
            resolved_headers[resolved_key] = resolved_value
            
            # Check if variables were not resolved
            import re
            if re.search(r'\{\{[A-Z0-9_]+\}\}', resolved_value):
                # Extract variable names that were not resolved
                for match in re.finditer(r'\{\{([A-Z0-9_]+)\}\}', resolved_value):
                    unresolved_vars.append(match.group(1))
        
        # If there are unresolved variables, return error
        if unresolved_vars:
            return jsonify({
                'success': False, 
                'error': f'未定義の変数: {", ".join(set(unresolved_vars))}。Variables画面で登録してください。'
            }), 400
        
        # Log resolved headers for debugging
        from flask import current_app
        current_app.logger.info(f"Test connection to {mcp_url}")
        current_app.logger.info(f"Resolved headers: {resolved_headers}")
        
        # Setup session with timeout and retries
        session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Test connection with MCP protocol (JSON-RPC 2.0)
        # First, try to initialize the session
        test_headers = resolved_headers.copy()
        test_headers['Content-Type'] = 'application/json'
        
        # Step 1: Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "AccelMCP",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        response = session.post(
            mcp_url, 
            json=init_request,
            headers=test_headers,
            timeout=10
        )
        
        # Check Content-Type to determine if SSE
        content_type = response.headers.get('Content-Type', '')
        if 'text/event-stream' in content_type:
            # SSE server
            return jsonify({
                'success': True,
                'message': 'Connection successful (SSE)',
                'server_type': 'sse'
            })
        
        # Check if response is valid
        if response.status_code == 200:
            # Try to parse as JSON-RPC response
            try:
                # Check if response has content
                if not response.text or response.text.strip() == '':
                    return jsonify({
                        'success': False,
                        'error': 'Server returned empty response'
                    })
                
                result = response.json()
                if 'result' in result:
                    # Initialize successful
                    server_info = result.get('result', {}).get('serverInfo', {})
                    return jsonify({
                        'success': True, 
                        'message': 'Connection successful',
                        'server_info': server_info
                    })
                elif 'error' in result:
                    error_msg = result['error'].get('message', 'Unknown error')
                    error_code = result['error'].get('code', 'unknown')
                    return jsonify({
                        'success': False,
                        'error': f'MCP Error ({error_code}): {error_msg}'
                    })
                else:
                    return jsonify({'success': True, 'message': 'Connection successful (non-standard response)'})
            except ValueError as e:
                # Not JSON - log response content for debugging
                from flask import current_app
                content_preview = response.text[:200] if response.text else '(empty)'
                current_app.logger.warning(f"Non-JSON response from {mcp_url}: {content_preview}")
                
                content_type = response.headers.get("Content-Type", "")
                return jsonify({
                    'success': False,
                    'error': f'Invalid JSON response: {str(e)}. Content-Type: {content_type}'
                })
        elif response.status_code == 405:
            return jsonify({
                'success': False, 
                'error': 'Method Not Allowed (405). The endpoint may not support MCP protocol or requires different authentication.'
            })
        else:
            return jsonify({
                'success': False, 
                'error': f'Server returned status code {response.status_code}: {response.text[:200]}'
            })
    
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Connection timeout'}), 200
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to server'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 200


@api_bp.route('/mcp-services/<int:mcp_service_id>/apps', methods=['GET', 'POST'])
@login_required
def mcp_service_apps(mcp_service_id):
    """Get all apps for an MCP service or create new app under MCP service"""
    mcp_service = McpService.query.get_or_404(mcp_service_id)
    
    if request.method == 'GET':
        return jsonify([app.to_dict() for app in mcp_service.apps])
    
    elif request.method == 'POST':
        data = request.get_json()
        service = Service(
            mcp_service_id=mcp_service_id,
            name=data['name'],
            service_type=data.get('service_type', 'api'),
            mcp_url=data.get('mcp_url'),
            common_headers=json.dumps(data.get('common_headers', {})),
            description=data.get('description', '')
        )
        db.session.add(service)
        db.session.commit()
        
        # MCPタイプの場合、自動でCapabilityを検出
        if service.service_type == 'mcp' and service.mcp_url:
            from app.services.mcp_discovery import discover_mcp_capabilities
            from flask import current_app
            try:
                current_app.logger.info(f"Starting MCP capability discovery for service {service.id}")
                tool_count = discover_mcp_capabilities(service.id, service.mcp_url)
                current_app.logger.info(f"Successfully discovered {tool_count} MCP tools")
            except Exception as e:
                current_app.logger.error(f"MCP capability discovery failed: {e}")
                # Capability検出失敗してもサービス登録は成功させる
        
        return jsonify(service.to_dict()), 201


@api_bp.route('/apps', methods=['GET', 'POST'])
@login_required
def apps():
    """Get all apps or create new app (legacy endpoint)"""
    if request.method == 'GET':
        services = Service.query.all()
        return jsonify([s.to_dict() for s in services])
    
    elif request.method == 'POST':
        data = request.get_json()
        # If mcp_service_id is provided, use it; otherwise create standalone (for backward compatibility)
        service = Service(
            mcp_service_id=data.get('mcp_service_id'),
            name=data['name'],
            service_type=data.get('service_type', 'api'),
            mcp_url=data.get('mcp_url'),
            common_headers=json.dumps(data.get('common_headers', {})),
            description=data.get('description', '')
        )
        db.session.add(service)
        db.session.commit()
        
        # MCPタイプの場合、自動でCapabilityを検出
        if service.service_type == 'mcp' and service.mcp_url:
            from app.services.mcp_discovery import discover_mcp_capabilities
            from flask import current_app
            try:
                current_app.logger.info(f"Starting MCP capability discovery for service {service.id}")
                tool_count = discover_mcp_capabilities(service.id, service.mcp_url)
                current_app.logger.info(f"Successfully discovered {tool_count} MCP tools")
            except Exception as e:
                current_app.logger.error(f"MCP capability discovery failed: {e}")
                # Capability検出失敗してもサービス登録は成功させる
        
        return jsonify(service.to_dict()), 201


@api_bp.route('/apps/<int:service_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def app_detail(service_id):
    """Get, update, or delete a specific app"""
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'GET':
        return jsonify(service.to_dict())
    
    elif request.method == 'PUT':
        data = request.get_json()
        service.name = data.get('name', service.name)
        service.service_type = data.get('service_type', service.service_type)
        service.mcp_url = data.get('mcp_url', service.mcp_url)
        service.common_headers = json.dumps(data.get('common_headers', {}))
        service.description = data.get('description', service.description)
        db.session.commit()
        
        # MCPタイプに変更された場合、自動でCapabilityを検出
        if service.service_type == 'mcp' and service.mcp_url:
            from app.services.mcp_discovery import discover_mcp_capabilities
            try:
                discover_mcp_capabilities(service.id, service.mcp_url)
            except Exception as e:
                print(f"MCP capability discovery failed: {e}")
        
        return jsonify(service.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(service)
        db.session.commit()
        return '', 204


@api_bp.route('/apps/<int:service_id>/toggle', methods=['POST'])
@login_required
def toggle_app(service_id):
    """Toggle app enabled/disabled status"""
    service = Service.query.get_or_404(service_id)
    service.is_enabled = not service.is_enabled
    db.session.commit()
    return jsonify(service.to_dict())


# ============= Capability API =============

@api_bp.route('/apps/<int:service_id>/capabilities', methods=['GET', 'POST'])
@login_required
def capabilities(service_id):
    """Get all capabilities for a service or create new capability"""
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'GET':
        capabilities = Capability.query.filter_by(app_id=service_id).all()
        return jsonify([c.to_dict() for c in capabilities])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # 同じアプリ内に同じ名前のCapabilityが存在しないかチェック
        existing = Capability.query.filter_by(
            app_id=service_id,
            name=data['name']
        ).first()
        if existing:
            return jsonify({'error': '同じ名前のCapabilityが既に存在します'}), 409
        
        capability = Capability(
            app_id=service_id,
            name=data['name'],
            capability_type=data['capability_type'],  # 'tool', 'resource', 'prompt', 'mcp_tool'
            url=data.get('url'),
            headers=json.dumps(data.get('headers', {})),
            body_params=json.dumps(data.get('body_params', {})),
            template_content=data.get('template_content'),
            description=data.get('description', '')
        )
        db.session.add(capability)
        db.session.flush()  # IDを取得するためにflush
        
        # 権限設定
        if 'account_ids' in data:
            for account_id in data['account_ids']:
                permission = AccountPermission(
                    capability_id=capability.id,
                    account_id=account_id
                )
                db.session.add(permission)
        
        db.session.commit()
        return jsonify(capability.to_dict()), 201


@api_bp.route('/capabilities/<int:capability_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def capability_detail(capability_id):
    """Get, update, or delete a specific capability"""
    capability = Capability.query.get_or_404(capability_id)
    
    if request.method == 'GET':
        return jsonify(capability.to_dict())
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # 名前を変更する場合、同じアプリ内に同じ名前のCapabilityが存在しないかチェック
        new_name = data.get('name', capability.name)
        if new_name != capability.name:
            existing = Capability.query.filter_by(
                app_id=capability.app_id,
                name=new_name
            ).filter(Capability.id != capability.id).first()
            if existing:
                return jsonify({'error': '同じ名前のCapabilityが既に存在します'}), 409
        
        capability.name = new_name
        capability.capability_type = data.get('capability_type', capability.capability_type)
        capability.url = data.get('url', capability.url)
        capability.headers = json.dumps(data.get('headers', {}))
        capability.body_params = json.dumps(data.get('body_params', {}))
        capability.template_content = data.get('template_content', capability.template_content)
        capability.description = data.get('description', capability.description)
        
        # 権限設定を更新
        if 'account_ids' in data:
            # 既存の権限を削除
            AccountPermission.query.filter_by(capability_id=capability.id).delete()
            # 新しい権限を追加
            for account_id in data['account_ids']:
                permission = AccountPermission(
                    capability_id=capability.id,
                    account_id=account_id
                )
                db.session.add(permission)
        
        db.session.commit()
        return jsonify(capability.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(capability)
        db.session.commit()
        return '', 204


@api_bp.route('/capabilities/<int:capability_id>/toggle', methods=['POST'])
@login_required
def toggle_capability(capability_id):
    """Toggle capability enabled/disabled status"""
    capability = Capability.query.get_or_404(capability_id)
    capability.is_enabled = not capability.is_enabled
    db.session.commit()
    return jsonify(capability.to_dict())


# ============= Connection Account API =============

@api_bp.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    """Get all connection accounts or create new account"""
    if request.method == 'GET':
        accounts = ConnectionAccount.query.all()
        return jsonify([a.to_dict() for a in accounts])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        account = ConnectionAccount(
            name=data['name'],
            bearer_token=secrets.token_urlsafe(32),
            notes=data.get('notes', '')
        )
        db.session.add(account)
        db.session.commit()
        return jsonify(account.to_dict()), 201


@api_bp.route('/accounts/<int:account_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def account_detail(account_id):
    """Get, update, or delete a specific connection account"""
    account = ConnectionAccount.query.get_or_404(account_id)
    
    if request.method == 'GET':
        return jsonify(account.to_dict())
    
    elif request.method == 'PUT':
        data = request.get_json()
        account.name = data.get('name', account.name)
        account.notes = data.get('notes', account.notes)
        
        db.session.commit()
        return jsonify(account.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(account)
        db.session.commit()
        return '', 204


@api_bp.route('/accounts/<int:account_id>/regenerate_token', methods=['POST'])
@login_required
def regenerate_token(account_id):
    """Regenerate account's bearer token"""
    account = ConnectionAccount.query.get_or_404(account_id)
    account.bearer_token = secrets.token_urlsafe(32)
    db.session.commit()
    return jsonify(account.to_dict())


# ============= Permission API =============

@api_bp.route('/accounts/<int:account_id>/permissions', methods=['GET', 'POST'])
@login_required
def account_permissions(account_id):
    """Get account permissions or add new permission (supports 3-tier)"""
    account = ConnectionAccount.query.get_or_404(account_id)
    
    if request.method == 'GET':
        permissions = AccountPermission.query.filter_by(account_id=account_id).all()
        return jsonify([p.to_dict() for p in permissions])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Determine which level of permission to add
        mcp_service_id = data.get('mcp_service_id')
        app_id = data.get('app_id')
        capability_id = data.get('capability_id')
        
        # Validate: exactly one must be provided
        provided = sum([bool(mcp_service_id), bool(app_id), bool(capability_id)])
        if provided != 1:
            return jsonify({'error': 'Exactly one of mcp_service_id, app_id, or capability_id must be provided'}), 400
        
        # Check if permission already exists
        existing = AccountPermission.query.filter_by(
            account_id=account_id,
            mcp_service_id=mcp_service_id,
            app_id=app_id,
            capability_id=capability_id
        ).first()
        
        if existing:
            return jsonify({'error': 'この権限は既に付与されています'}), 400
        
        # Verify the resource exists
        if mcp_service_id:
            McpService.query.get_or_404(mcp_service_id)
        elif app_id:
            Service.query.get_or_404(app_id)
        elif capability_id:
            Capability.query.get_or_404(capability_id)
        
        permission = AccountPermission(
            account_id=account_id,
            mcp_service_id=mcp_service_id,
            app_id=app_id,
            capability_id=capability_id
        )
        db.session.add(permission)
        db.session.commit()
        return jsonify(permission.to_dict()), 201


@api_bp.route('/permissions/<int:permission_id>', methods=['DELETE'])
@login_required
def permission_delete(permission_id):
    """Delete a permission"""
    permission = AccountPermission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    return '', 204


@api_bp.route('/capabilities/<int:capability_id>/permissions', methods=['GET', 'PUT'])
@login_required
def capability_permissions(capability_id):
    """Get or update permissions for a capability"""
    capability = Capability.query.get_or_404(capability_id)
    
    if request.method == 'GET':
        # Get all accounts with permissions for this capability
        permissions = AccountPermission.query.filter_by(capability_id=capability_id).all()
        enabled_account_ids = [p.account_id for p in permissions]
        
        # Get enabled accounts (with permission)
        enabled_accounts = ConnectionAccount.query.filter(
            ConnectionAccount.id.in_(enabled_account_ids)
        ).all()
        
        # Get disabled accounts (without permission)
        disabled_accounts = ConnectionAccount.query.filter(
            ~ConnectionAccount.id.in_(enabled_account_ids)
        ).all()
        
        return jsonify({
            'enabled': [a.to_dict() for a in enabled_accounts],
            'disabled': [a.to_dict() for a in disabled_accounts]
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        account_ids = data.get('account_ids', [])
        
        # Delete all existing permissions for this capability
        AccountPermission.query.filter_by(capability_id=capability_id).delete()
        
        # Add new permissions
        for account_id in account_ids:
            # Verify account exists
            account = ConnectionAccount.query.filter_by(id=account_id).first()
            if account:
                permission = AccountPermission(account_id=account_id, capability_id=capability_id)
                db.session.add(permission)
        
        db.session.commit()
        return jsonify({'message': '権限設定を更新しました'}), 200


# ============= Settings API =============

@api_bp.route('/settings/language', methods=['GET', 'POST'])
@login_required
def language_setting():
    """Get or set language preference"""
    if request.method == 'GET':
        setting = AdminSettings.query.filter_by(setting_key='language').first()
        if setting:
            language = setting.setting_value
            is_initialized = True
        else:
            language = None
            is_initialized = False
        return jsonify({'language': language, 'is_initialized': is_initialized})
    
    elif request.method == 'POST':
        data = request.get_json()
        language = data.get('language', 'ja')
        
        # Validate language
        if language not in ['ja', 'en']:
            return jsonify({'error': 'Invalid language'}), 400
        
        # Update or create setting
        setting = AdminSettings.query.filter_by(setting_key='language').first()
        if setting:
            setting.setting_value = language
        else:
            setting = AdminSettings(setting_key='language', setting_value=language)
            db.session.add(setting)
        
        db.session.commit()
        return jsonify({'message': 'Language setting updated', 'language': language}), 200


# ============= Template API =============

@api_bp.route('/mcp-templates', methods=['GET'])
@login_required
def templates():
    """Get all service templates"""
    from app.models.models import McpServiceTemplate
    
    template_type = request.args.get('type')  # 'builtin' or 'custom'
    category = request.args.get('category')
    
    query = McpServiceTemplate.query
    if template_type:
        query = query.filter_by(template_type=template_type)
    if category:
        query = query.filter_by(category=category)
    
    templates = query.all()
    return jsonify([t.to_dict() for t in templates])


@api_bp.route('/mcp-templates/<int:template_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def template_detail(template_id):
    """Get, update, or delete a specific template"""
    from app.models.models import McpServiceTemplate
    
    template = McpServiceTemplate.query.get_or_404(template_id)
    
    if request.method == 'GET':
        result = template.to_dict()
        # Include capability templates
        result['capabilities'] = [c.to_dict() for c in template.capability_templates]
        return jsonify(result)
    
    elif request.method == 'PUT':
        # Only custom templates can be updated
        if template.template_type != 'custom':
            return jsonify({'error': 'Cannot modify builtin templates'}), 403
        
        data = request.get_json()
        template.name = data.get('name', template.name)
        template.service_type = data.get('service_type', template.service_type)
        template.description = data.get('description', template.description)
        template.common_headers = json.dumps(data.get('common_headers', {}))
        template.icon = data.get('icon', template.icon)
        template.category = data.get('category', template.category)
        db.session.commit()
        return jsonify(template.to_dict())
    
    elif request.method == 'DELETE':
        # Only custom templates can be deleted
        if template.template_type != 'custom':
            return jsonify({'error': 'Cannot delete builtin templates'}), 403
        
        db.session.delete(template)
        db.session.commit()
        return '', 204


@api_bp.route('/mcp-templates', methods=['POST'])
@login_required
def create_template():
    """Create a new custom template"""
    from app.models.models import McpServiceTemplate, McpCapabilityTemplate
    
    data = request.get_json()
    
    template = McpServiceTemplate(
        name=data['name'],
        template_type='custom',
        service_type=data.get('service_type', 'api'),
        description=data.get('description', ''),
        common_headers=json.dumps(data.get('common_headers', {})),
        icon=data.get('icon', '📦'),
        category=data.get('category', 'Custom')
    )
    db.session.add(template)
    db.session.flush()  # Get template ID
    
    # Add capability templates
    for cap_data in data.get('capabilities', []):
        capability = McpCapabilityTemplate(
            service_template_id=template.id,
            name=cap_data['name'],
            capability_type=cap_data.get('capability_type', 'tool'),
            url=cap_data.get('url', ''),
            headers=json.dumps(cap_data.get('headers', {})),
            body_params=json.dumps(cap_data.get('body_params', {})),
            template_content=cap_data.get('template_content', ''),
            description=cap_data.get('description', '')
        )
        db.session.add(capability)
    
    db.session.commit()
    return jsonify(template.to_dict()), 201


@api_bp.route('/mcp-templates/<int:template_id>/capabilities', methods=['GET', 'POST'])
@login_required
def template_capabilities(template_id):
    """Get or add capabilities to a template"""
    from app.models.models import McpServiceTemplate, McpCapabilityTemplate
    
    template = McpServiceTemplate.query.get_or_404(template_id)
    
    if request.method == 'GET':
        capabilities = McpCapabilityTemplate.query.filter_by(service_template_id=template_id).all()
        return jsonify([c.to_dict() for c in capabilities])
    
    elif request.method == 'POST':
        # Only custom templates can be modified
        if template.template_type != 'custom':
            return jsonify({'error': 'Cannot modify builtin templates'}), 403
        
        data = request.get_json()
        capability = McpCapabilityTemplate(
            service_template_id=template_id,
            name=data['name'],
            capability_type=data.get('capability_type', 'tool'),
            url=data.get('url', ''),
            headers=json.dumps(data.get('headers', {})),
            body_params=json.dumps(data.get('body_params', {})),
            template_content=data.get('template_content', ''),
            description=data.get('description', '')
        )
        db.session.add(capability)
        db.session.commit()
        return jsonify(capability.to_dict()), 201


@api_bp.route('/mcp-template-capabilities/<int:capability_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def template_capability_detail(capability_id):
    """Get, update, or delete a template capability"""
    from app.models.models import McpCapabilityTemplate
    
    capability = McpCapabilityTemplate.query.get_or_404(capability_id)
    
    if request.method == 'GET':
        return jsonify(capability.to_dict())
    
    elif request.method == 'PUT':
        # Check if parent template is custom
        if capability.service_template.template_type != 'custom':
            return jsonify({'error': 'Cannot modify builtin templates'}), 403
        
        data = request.get_json()
        capability.name = data.get('name', capability.name)
        capability.capability_type = data.get('capability_type', capability.capability_type)
        capability.url = data.get('url', capability.url)
        capability.headers = json.dumps(data.get('headers', {}))
        capability.body_params = json.dumps(data.get('body_params', {}))
        capability.template_content = data.get('template_content', capability.template_content)
        capability.description = data.get('description', capability.description)
        db.session.commit()
        return jsonify(capability.to_dict())
    
    elif request.method == 'DELETE':
        # Check if parent template is custom
        if capability.service_template.template_type != 'custom':
            return jsonify({'error': 'Cannot delete builtin templates'}), 403
        
        db.session.delete(capability)
        db.session.commit()
        return '', 204


@api_bp.route('/mcp-templates/<int:template_id>/export', methods=['GET'])
@login_required
def export_template(template_id):
    """Export template as JSON"""
    from app.models.models import McpServiceTemplate
    
    template = McpServiceTemplate.query.get_or_404(template_id)
    return jsonify(template.to_export_dict())


@api_bp.route('/mcp-templates/import', methods=['POST'])
@login_required
def import_template():
    """Import template from JSON"""
    from app.models.models import McpServiceTemplate, McpCapabilityTemplate
    
    data = request.get_json()
    
    # Create template as custom
    template = McpServiceTemplate(
        name=data['name'],
        template_type='custom',
        service_type=data.get('service_type', 'api'),
        description=data.get('description', ''),
        common_headers=json.dumps(data.get('common_headers', {})),
        icon=data.get('icon', '📦'),
        category=data.get('category', 'Custom')
    )
    db.session.add(template)
    db.session.flush()
    
    # Add capabilities
    for cap_data in data.get('capabilities', []):
        capability = McpCapabilityTemplate(
            service_template_id=template.id,
            name=cap_data['name'],
            capability_type=cap_data.get('capability_type', 'tool'),
            url=cap_data.get('url', ''),
            headers=json.dumps(cap_data.get('headers', {})),
            body_params=json.dumps(cap_data.get('body_params', {})),
            template_content=cap_data.get('template_content', ''),
            description=cap_data.get('description', '')
        )
        db.session.add(capability)
    
    db.session.commit()
    return jsonify(template.to_dict()), 201


@api_bp.route('/mcp-templates/<int:template_id>/apply', methods=['POST'])
@login_required
def apply_template(template_id):
    """Apply template to create a new app in selected MCP service"""
    from app.models.models import McpServiceTemplate, McpService
    
    template = McpServiceTemplate.query.get_or_404(template_id)
    data = request.get_json()
    
    mcp_service_id = data.get('mcp_service_id')
    if not mcp_service_id:
        return jsonify({'error': 'MCP service ID is required'}), 400
    
    # Check if MCP service exists
    mcp_service = McpService.query.get_or_404(mcp_service_id)
    
    try:
        # Create app from template
        service = Service(
            name=data.get('name', template.name),
            service_type=template.service_type,
            common_headers=template.common_headers,
            description=data.get('description', template.description),
            mcp_service_id=mcp_service_id
        )
        db.session.add(service)
        db.session.flush()
        
        # Create capabilities from template
        for cap_template in template.capability_templates:
            capability = Capability(
                app_id=service.id,
                name=cap_template.name,
                capability_type=cap_template.capability_type,
                url=cap_template.url,
                headers=cap_template.headers,
                body_params=cap_template.body_params,
                template_content=cap_template.template_content,
                description=cap_template.description
            )
            db.session.add(capability)
        
        db.session.commit()
        return jsonify(service.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= Variables API =============

@api_bp.route('/variables', methods=['GET', 'POST'])
@login_required
def variables():
    """Get all variables or create new variable"""
    if request.method == 'GET':
        variables = Variable.query.all()
        return jsonify([v.to_dict() for v in variables])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Check for duplicate name
        if Variable.query.filter_by(name=data['name']).first():
            return jsonify({'error': '同じ名前の変数が既に存在します'}), 409
        
        source_type = data.get('source_type', 'value')
        
        variable = Variable(
            name=data['name'],
            value_type=data.get('value_type', 'string'),
            source_type=source_type,
            description=data.get('description', ''),
            is_secret=data.get('is_secret', True)
        )
        
        if source_type == 'env':
            variable.env_var_name = data.get('env_var_name', '')
            variable.value = ''  # 環境変数の場合は値を空にする
        else:
            variable.set_value(data['value'])
        
        db.session.add(variable)
        db.session.commit()
        return jsonify(variable.to_dict()), 201


@api_bp.route('/variables/check-env', methods=['POST'])
@login_required
def check_env_variable():
    """Check if environment variable exists"""
    import os
    data = request.get_json()
    env_var_name = data.get('env_var_name', '')
    
    if not env_var_name:
        return jsonify({'exists': False}), 200
    
    # Check if environment variable exists and has a value
    env_value = os.environ.get(env_var_name)
    exists = env_value is not None and env_value != ''
    
    return jsonify({'exists': exists}), 200


@api_bp.route('/variables/<int:variable_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def variable_detail(variable_id):
    """Get, update, or delete a specific variable"""
    variable = Variable.query.get_or_404(variable_id)
    
    if request.method == 'GET':
        # include_value=True to show actual value for editing
        return jsonify(variable.to_dict(include_value=True))
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Check for duplicate name (exclude current variable)
        new_name = data.get('name', variable.name)
        if new_name != variable.name:
            existing = Variable.query.filter_by(name=new_name).filter(Variable.id != variable.id).first()
            if existing:
                return jsonify({'error': '同じ名前の変数が既に存在します'}), 409
        
        variable.name = new_name
        variable.value_type = data.get('value_type', variable.value_type)
        variable.source_type = data.get('source_type', variable.source_type)
        variable.description = data.get('description', variable.description)
        variable.is_secret = data.get('is_secret', variable.is_secret)
        
        if variable.source_type == 'env':
            variable.env_var_name = data.get('env_var_name', variable.env_var_name)
            variable.value = ''  # 環境変数の場合は値を空にする
        else:
            if 'value' in data:
                variable.set_value(data['value'])
        
        db.session.commit()
        return jsonify(variable.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(variable)
        db.session.commit()
        return '', 204


# ============= Hierarchical Access Control API =============

@api_bp.route('/mcp-services/<int:mcp_service_id>/access-control', methods=['PUT'])
@login_required
def mcp_service_access_control(mcp_service_id):
    """Toggle MCP service access control (public/restricted)"""
    mcp_service = McpService.query.get_or_404(mcp_service_id)
    
    data = request.get_json()
    access_control = data.get('access_control')
    
    if access_control not in ['public', 'restricted']:
        return jsonify({'error': 'access_control must be "public" or "restricted"'}), 400
    
    mcp_service.access_control = access_control
    db.session.commit()
    
    return jsonify(mcp_service.to_dict())


@api_bp.route('/apps/<int:app_id>/access-control', methods=['PUT'])
@login_required
def app_access_control(app_id):
    """Toggle app access control (public/restricted)"""
    app = Service.query.get_or_404(app_id)
    
    data = request.get_json()
    access_control = data.get('access_control')
    
    if access_control not in ['public', 'restricted']:
        return jsonify({'error': 'access_control must be "public" or "restricted"'}), 400
    
    app.access_control = access_control
    db.session.commit()
    
    return jsonify(app.to_dict())


@api_bp.route('/capabilities/<int:capability_id>/access-control', methods=['PUT'])
@login_required
def capability_access_control(capability_id):
    """Toggle capability access control (public/restricted)"""
    capability = Capability.query.get_or_404(capability_id)
    
    data = request.get_json()
    access_control = data.get('access_control')
    
    if access_control not in ['public', 'restricted']:
        return jsonify({'error': 'access_control must be "public" or "restricted"'}), 400
    
    capability.access_control = access_control
    db.session.commit()
    
    return jsonify(capability.to_dict())


@api_bp.route('/mcp-services/<int:mcp_service_id>/permissions', methods=['GET', 'POST'])
@login_required
def mcp_service_permissions(mcp_service_id):
    """Get or add MCP service level permissions"""
    mcp_service = McpService.query.get_or_404(mcp_service_id)
    
    if request.method == 'GET':
        # Get all accounts with permissions for this MCP service
        permissions = AccountPermission.query.filter_by(mcp_service_id=mcp_service_id).all()
        enabled_account_ids = [p.account_id for p in permissions]
        
        # Get enabled accounts (with permission)
        enabled_accounts = ConnectionAccount.query.filter(
            ConnectionAccount.id.in_(enabled_account_ids)
        ).all() if enabled_account_ids else []
        
        # Get disabled accounts (without permission)
        disabled_accounts = ConnectionAccount.query.filter(
            ~ConnectionAccount.id.in_(enabled_account_ids)
        ).all() if enabled_account_ids else ConnectionAccount.query.all()
        
        return jsonify({
            'enabled': [a.to_dict() for a in enabled_accounts],
            'disabled': [a.to_dict() for a in disabled_accounts]
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        account_ids = data.get('account_ids', [])
        
        # Delete all existing permissions for this MCP service
        AccountPermission.query.filter_by(mcp_service_id=mcp_service_id).delete()
        
        # Add new permissions
        for account_id in account_ids:
            # Verify account exists
            account = ConnectionAccount.query.filter_by(id=account_id).first()
            if account:
                permission = AccountPermission(
                    account_id=account_id,
                    mcp_service_id=mcp_service_id
                )
                db.session.add(permission)
        
        db.session.commit()
        return jsonify({'message': 'MCP service permissions updated'}), 200
        db.session.add(permission)
        db.session.commit()
        
        return jsonify(permission.to_dict()), 201


@api_bp.route('/apps/<int:app_id>/permissions', methods=['GET', 'POST'])
@login_required
def app_permissions(app_id):
    """Get or add app level permissions"""
    app = Service.query.get_or_404(app_id)
    
    if request.method == 'GET':
        # Get all accounts with permissions for this app
        permissions = AccountPermission.query.filter_by(app_id=app_id).all()
        enabled_account_ids = [p.account_id for p in permissions]
        
        # Get enabled accounts (with permission)
        enabled_accounts = ConnectionAccount.query.filter(
            ConnectionAccount.id.in_(enabled_account_ids)
        ).all() if enabled_account_ids else []
        
        # Get disabled accounts (without permission)
        disabled_accounts = ConnectionAccount.query.filter(
            ~ConnectionAccount.id.in_(enabled_account_ids)
        ).all() if enabled_account_ids else ConnectionAccount.query.all()
        
        return jsonify({
            'enabled': [a.to_dict() for a in enabled_accounts],
            'disabled': [a.to_dict() for a in disabled_accounts]
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        account_ids = data.get('account_ids', [])
        
        # Delete all existing permissions for this app
        AccountPermission.query.filter_by(app_id=app_id).delete()
        
        # Add new permissions
        for account_id in account_ids:
            # Verify account exists
            account = ConnectionAccount.query.filter_by(id=account_id).first()
            if account:
                permission = AccountPermission(
                    account_id=account_id,
                    app_id=app_id
                )
                db.session.add(permission)
        
        db.session.commit()
        return jsonify({'message': 'App permissions updated'}), 200


@api_bp.route('/accounts/<int:account_id>/permissions/by-level', methods=['GET'])
@login_required
def account_permissions_by_level(account_id):
    """Get account permissions grouped by level (mcp_service, app, capability)"""
    account = ConnectionAccount.query.get_or_404(account_id)
    
    permissions = AccountPermission.query.filter_by(account_id=account_id).all()
    
    result = {
        'mcp_service': [],
        'app': [],
        'capability': []
    }
    
    for perm in permissions:
        level = perm.get_permission_level()
        if level:
            result[level].append(perm.to_dict())
    
    return jsonify(result)

