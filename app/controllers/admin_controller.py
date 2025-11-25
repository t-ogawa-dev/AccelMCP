"""
Admin Controller
Handles admin panel routes (dashboard, services, accounts, capabilities)
"""
from flask import Blueprint, render_template
from app.controllers.auth_controller import login_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


# ============= MCP Service Management Routes =============

@admin_bp.route('/mcp-services')
@login_required
def mcp_services_list():
    """MCP services list page"""
    return render_template('mcp_services/list.html')


@admin_bp.route('/mcp-services/new')
@login_required
def mcp_service_new():
    """New MCP service page"""
    return render_template('mcp_services/new.html')


@admin_bp.route('/mcp-services/<int:mcp_service_id>')
@login_required
def mcp_service_detail(mcp_service_id):
    """MCP service detail page"""
    return render_template('mcp_services/detail.html', mcp_service_id=mcp_service_id)


@admin_bp.route('/mcp-services/<int:mcp_service_id>/edit')
@login_required
def mcp_service_edit(mcp_service_id):
    """Edit MCP service page"""
    return render_template('mcp_services/edit.html', mcp_service_id=mcp_service_id)


# ============= Service Management Routes =============

@admin_bp.route('/mcp-services/<int:mcp_service_id>/apps')
@login_required
def services_list(mcp_service_id):
    """Services list page"""
    return render_template('services/list.html', mcp_service_id=mcp_service_id)


@admin_bp.route('/mcp-services/<int:mcp_service_id>/apps/new')
@login_required
def service_new(mcp_service_id):
    """New service page"""
    return render_template('services/new.html', mcp_service_id=mcp_service_id)


@admin_bp.route('/mcp-services/<int:mcp_service_id>/apps/<int:service_id>')
@login_required
def service_detail(mcp_service_id, service_id):
    """Service detail page"""
    return render_template('services/detail.html', mcp_service_id=mcp_service_id, service_id=service_id)


@admin_bp.route('/mcp-services/<int:mcp_service_id>/apps/<int:service_id>/edit')
@login_required
def service_edit(mcp_service_id, service_id):
    """Service edit page"""
    return render_template('services/edit.html', mcp_service_id=mcp_service_id, service_id=service_id)


@admin_bp.route('/mcp-services/<int:mcp_service_id>/apps/<int:service_id>/capabilities')
@login_required
def service_capabilities(mcp_service_id, service_id):
    """Service capabilities page"""
    return render_template('services/capabilities.html', mcp_service_id=mcp_service_id, service_id=service_id)


@admin_bp.route('/mcp-services/<int:mcp_service_id>/apps/<int:service_id>/capabilities/new')
@login_required
def capability_new(mcp_service_id, service_id):
    """New capability page"""
    return render_template('capabilities/new.html', mcp_service_id=mcp_service_id, service_id=service_id)


@admin_bp.route('/capabilities/<int:capability_id>')
@login_required
def capability_detail(capability_id):
    """Capability detail page"""
    return render_template('capabilities/detail.html', capability_id=capability_id)


@admin_bp.route('/capabilities/<int:capability_id>/edit')
@login_required
def capability_edit(capability_id):
    """Capability edit page"""
    return render_template('capabilities/edit.html', capability_id=capability_id)


# ============= Account Management Routes =============

@admin_bp.route('/accounts')
@login_required
def accounts_list():
    """Connection accounts list page"""
    return render_template('accounts/list.html')


@admin_bp.route('/accounts/new')
@login_required
def account_new():
    """New connection account page"""
    return render_template('accounts/new.html')


@admin_bp.route('/accounts/<int:account_id>')
@login_required
def account_detail(account_id):
    """Connection account detail page"""
    return render_template('accounts/detail.html', account_id=account_id)


# ============= Variables Management Routes =============

@admin_bp.route('/variables')
@login_required
def variables_list():
    """Variables list page"""
    return render_template('variables/list.html')


@admin_bp.route('/variables/new')
@login_required
def variable_new():
    """New variable page"""
    return render_template('variables/new.html')


@admin_bp.route('/variables/<int:variable_id>/edit')
@login_required
def variable_edit(variable_id):
    """Edit variable page"""
    return render_template('variables/edit.html', variable_id=variable_id)


# ============= Template Management Routes =============

@admin_bp.route('/mcp-templates')
@login_required
def templates_list():
    """Templates list page (builtin and custom tabs)"""
    return render_template('mcp_templates/list.html')


@admin_bp.route('/mcp-templates/new')
@login_required
def template_new():
    """New custom template page"""
    return render_template('mcp_templates/new.html')


@admin_bp.route('/mcp-templates/<int:template_id>')
@login_required
def template_detail(template_id):
    """Template detail page"""
    return render_template('mcp_templates/detail.html', template_id=template_id)


@admin_bp.route('/mcp-templates/<int:template_id>/edit')
@login_required
def template_edit(template_id):
    """Template edit page"""
    return render_template('mcp_templates/edit.html', template_id=template_id)


@admin_bp.route('/mcp-templates/<int:template_id>/capabilities')
@login_required
def template_capabilities(template_id):
    """Template capabilities management page"""
    return render_template('mcp_templates/capabilities.html', template_id=template_id)


@admin_bp.route('/mcp-templates/<int:template_id>/capabilities/new')
@login_required
def template_capability_new(template_id):
    """New capability page"""
    return render_template('mcp_templates/capability_new.html', template_id=template_id)


@admin_bp.route('/mcp-templates/<int:template_id>/capabilities/<int:capability_id>')
@login_required
def template_capability_detail(template_id, capability_id):
    """Capability detail page"""
    return render_template('mcp_templates/capability_detail.html', template_id=template_id, capability_id=capability_id)


@admin_bp.route('/mcp-templates/<int:template_id>/capabilities/<int:capability_id>/edit')
@login_required
def template_capability_edit(template_id, capability_id):
    """Edit capability page"""
    return render_template('mcp_templates/capability_edit.html', template_id=template_id, capability_id=capability_id)
