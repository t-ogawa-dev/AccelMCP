// capabilities/detail.js - Capability Detail Page
const capabilityId = parseInt(window.location.pathname.split('/')[2]);

async function loadCapability() {
    const response = await fetch(`/api/capabilities/${capabilityId}`);
    const cap = await response.json();
    
    // Update breadcrumb links
    if (cap.mcp_service_id && cap.service_id) {
        const mcpServiceId = cap.mcp_service_id;
        const serviceId = cap.service_id;
        
        document.getElementById('mcp-service-link').href = `/mcp-services/${mcpServiceId}`;
        document.getElementById('apps-link').href = `/mcp-services/${mcpServiceId}/apps`;
        document.getElementById('service-link').href = `/mcp-services/${mcpServiceId}/apps/${serviceId}`;
        document.getElementById('capabilities-link').href = `/mcp-services/${mcpServiceId}/apps/${serviceId}/capabilities`;
        
        // Fetch service name for breadcrumb
        try {
            const serviceResponse = await fetch(`/api/apps/${serviceId}`);
            const service = await serviceResponse.json();
            if (service.mcp_service_name) {
                document.getElementById('mcp-service-link').textContent = service.mcp_service_name;
            }
        } catch (e) {
            console.error('Failed to fetch service info for breadcrumb:', e);
        }
    }
    
    document.getElementById('edit-link').href = `/capabilities/${capabilityId}/edit`;
    
    const container = document.getElementById('capability-detail');
    container.innerHTML = `
        <div class="detail-section">
            <h2>${cap.name}</h2>
            <span class="badge badge-${cap.capability_type}">${cap.capability_type.toUpperCase()}</span>
            ${cap.description ? `<p class="text-muted">${cap.description}</p>` : ''}
        </div>
        
        <div class="detail-section">
            <h3>${t("capability_basic_info")}</h3>
            <table class="detail-table">
                <tr>
                    <th>${t("capability_type_detail")}</th>
                    <td><span class="badge badge-${cap.capability_type}">${cap.capability_type.toUpperCase()}</span></td>
                </tr>
                <tr>
                    <th>${t('access_control')}</th>
                    <td>
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <label class="toggle-switch">
                                <input type="checkbox" id="access-control-toggle" onchange="toggleAccessControl()" ${cap.access_control === 'public' ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                            <span id="access-control-label"></span>
                        </div>
                        <small id="access-control-description" style="display: block; margin-top: 5px; color: #666;"></small>
                    </td>
                </tr>
                <tr>
                    <th>${t("capability_method_label")}</th>
                    <td><span class="badge badge-method">${cap.headers['X-HTTP-Method'] || 'POST'}</span></td>
                </tr>
                <tr>
                    <th>${t("capability_url_label")}</th>
                    <td><code>${cap.url || 'N/A'}</code></td>
                </tr>
                <tr>
                    <th>${t("capability_registered_at")}</th>
                    <td>${new Date(cap.created_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
                <tr>
                    <th>${t("capability_updated_at")}</th>
                    <td>${new Date(cap.updated_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
            </table>
        </div>
        
        <div class="detail-section">
            <h3>${t("capability_headers_params")}</h3>
            <pre class="code-block">${JSON.stringify(cap.headers, null, 2)}</pre>
        </div>
        
        <div class="detail-section">
            <h3>${t("capability_body_params_label")}</h3>
            <pre class="code-block">${JSON.stringify(cap.body_params, null, 2)}</pre>
        </div>
    `;
    
    // Update access control UI
    const isPublic = cap.access_control === 'public';
    updateAccessControlUI(isPublic);
    
    // Load permissions if restricted
    if (!isPublic) {
        document.getElementById('permissions-section').style.display = 'block';
        loadPermissions();
    }
}

function updateAccessControlUI(isPublic) {
    const label = document.getElementById('access-control-label');
    const description = document.getElementById('access-control-description');
    
    if (isPublic) {
        label.textContent = t('access_control_public');
        label.style.color = '#10b981';
        description.textContent = t('access_control_public_desc');
    } else {
        label.textContent = t('access_control_restricted');
        label.style.color = '#f59e0b';
        description.textContent = t('access_control_restricted_desc');
    }
}

async function toggleAccessControl() {
    const toggle = document.getElementById('access-control-toggle');
    const isPublic = toggle.checked;
    const newAccessControl = isPublic ? 'public' : 'restricted';
    
    try {
        const response = await fetch(`/api/capabilities/${capabilityId}/access-control`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_control: newAccessControl })
        });
        
        if (!response.ok) throw new Error('Failed to update access control');
        
        updateAccessControlUI(isPublic);
        
        // Show/hide permissions section
        const permissionsSection = document.getElementById('permissions-section');
        if (isPublic) {
            permissionsSection.style.display = 'none';
        } else {
            permissionsSection.style.display = 'block';
            loadPermissions();
        }
    } catch (error) {
        console.error('Error:', error);
        alert(t('permission_error'));
        toggle.checked = !isPublic; // Revert
    }
}

async function loadPermissions() {
    try {
        // Use the same endpoint as before for capability permissions
        const response = await fetch(`/api/capabilities/${capabilityId}/permissions`);
        const data = await response.json();
        
        const container = document.getElementById('permissions-list');
        
        // data might be { enabled: [...], disabled: [...] } or just an array
        const permissions = Array.isArray(data) ? data : (data.enabled || []);
        
        if (permissions.length === 0) {
            container.innerHTML = `<p data-i18n="permissions_empty">${t('permissions_empty')}</p>`;
            return;
        }
        
        container.innerHTML = permissions.map(perm => {
            const accountName = perm.account ? perm.account.name : (perm.name || 'Unknown');
            const accountId = perm.account ? perm.account.id : perm.id;
            
            return `
                <div class="permission-item">
                    <div>
                        <strong>${accountName}</strong>
                        <br>
                        <small style="color: #666;">${t('permission_level_capability')}</small>
                    </div>
                    <button onclick="deletePermissionByAccount(${accountId})" class="btn btn-sm btn-danger">
                        ${t('button_delete')}
                    </button>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading permissions:', error);
    }
}

let allAccounts = [];

async function showAddPermissionModal() {
    const response = await fetch('/api/accounts');
    allAccounts = await response.json();
    
    const select = document.getElementById('permission-account-select');
    select.innerHTML = '<option value="">選択してください</option>' + 
        allAccounts.map(acc => `<option value="${acc.id}">${acc.name</option>`).join('');
    
    document.getElementById('add-permission-modal').style.display = 'flex';
}

function closeAddPermissionModal() {
    document.getElementById('add-permission-modal').style.display = 'none';
}

async function addPermission() {
    const accountId = document.getElementById('permission-account-select').value;
    
    if (!accountId) {
        alert('アカウントを選択してください');
        return;
    }
    
    try {
        const response = await fetch(`/api/accounts/${accountId}/permissions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ capability_id: capabilityId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add permission');
        }
        
        closeAddPermissionModal();
        loadPermissions();
        alert(t('permission_added'));
    } catch (error) {
        console.error('Error:', error);
        alert(error.message || t('permission_error'));
    }
}

async function deletePermissionByAccount(accountId) {
    if (!confirm(t('confirm_delete'))) return;
    
    try {
        // Find the permission ID for this account and capability
        const permissionsResponse = await fetch(`/api/accounts/${accountId}/permissions`);
        const permissions = await permissionsResponse.json();
        const permission = permissions.find(p => p.capability_id === capabilityId);
        
        if (!permission) {
            throw new Error('Permission not found');
        }
        
        const response = await fetch(`/api/permissions/${permission.id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete permission');
        
        loadPermissions();
        alert(t('permission_deleted'));
    } catch (error) {
        console.error('Error:', error);
        alert(t('permission_error'));
    }
}

// Initialize language and load capability detail
(async () => {
    await initLanguageSwitcher();
    loadCapability();
})();

