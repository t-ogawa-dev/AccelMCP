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


# ============= Service Management Routes =============

@admin_bp.route('/services')
@login_required
def services_list():
    """Services list page"""
    return render_template('services/list.html')


@admin_bp.route('/services/new')
@login_required
def service_new():
    """New service page"""
    return render_template('services/new.html')


@admin_bp.route('/services/<int:service_id>')
@login_required
def service_detail(service_id):
    """Service detail page"""
    return render_template('services/detail.html', service_id=service_id)


@admin_bp.route('/services/<int:service_id>/edit')
@login_required
def service_edit(service_id):
    """Service edit page"""
    return render_template('services/edit.html', service_id=service_id)


@admin_bp.route('/services/<int:service_id>/capabilities')
@login_required
def service_capabilities(service_id):
    """Service capabilities page"""
    return render_template('services/capabilities.html', service_id=service_id)


@admin_bp.route('/services/<int:service_id>/capabilities/new')
@login_required
def capability_new(service_id):
    """New capability page"""
    return render_template('capabilities/new.html', service_id=service_id)


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
