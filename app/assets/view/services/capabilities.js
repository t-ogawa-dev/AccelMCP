// services/capabilities.js - Service Capabilities List
const pathParts = window.location.pathname.split('/');
const mcpServiceId = parseInt(pathParts[2]);
const serviceId = parseInt(pathParts[4]);
let isMcpType = false;
let baseUrl = '';

async function loadCapabilities() {
    const response = await fetch(`/api/apps/${serviceId}/capabilities`);
    const capabilities = await response.json();
    
    const container = document.getElementById('capabilities-list');
    
    if (capabilities.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('capability_empty')}</div>`;
        return;
    }
    
    container.innerHTML = capabilities.map(cap => {
        // Build full URL display: baseUrl + endpoint_path
        let urlDisplay = cap.url || 'N/A';
        if (baseUrl && cap.url && !cap.url.startsWith('http')) {
            // If cap.url is a relative path, combine with baseUrl
            const separator = baseUrl.endsWith('/') || cap.url.startsWith('/') ? '' : '/';
            urlDisplay = `<span style="color: #666;">${baseUrl}</span>${separator}<span style="font-weight: 600;">${cap.url}</span>`;
        }
        
        return `
        <div class="list-item ${!cap.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/capabilities/${cap.id}">${cap.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge badge-${cap.capability_type}">${cap.capability_type.toUpperCase()}</span>
                    ${!cap.is_enabled ? `<span class="status-badge disabled">${t('status_disabled')}</span>` : `<span class="status-badge enabled">${t('status_enabled')}</span>`}
                    ${(cap.access_control === 'restricted') ? `<span class="badge badge-access-restricted">${t('access_control_restricted')}</span>` : `<span class="badge badge-access-public">${t('access_control_public')}</span>`}
                    <span class="text-muted" style="font-family: monospace; font-size: 0.9em;">${urlDisplay}</span>
                </div>
                ${cap.description ? `<p class="text-muted">${cap.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <label class="toggle-switch">
                    <input type="checkbox" ${cap.is_enabled ? 'checked' : ''} onchange="toggleCapability(${cap.id})">
                    <span class="toggle-slider"></span>
                </label>
                <a href="/capabilities/${cap.id}/edit" class="btn btn-sm">${t('button_edit')}</a>
                ${!isMcpType ? `<button onclick="deleteCapability(${cap.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>` : ''}
            </div>
        </div>
    `;
    }).join('');
}

async function toggleCapability(id) {
    try {
        const response = await fetch(`/api/capabilities/${id}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadCapabilities();
        } else {
            const error = await response.json();
            alert('切り替えに失敗しました: ' + (error.error || 'Unknown error'));
        }
    } catch (e) {
        alert('切り替えに失敗しました: ' + e.message);
    }
}

async function deleteCapability(id) {
    if (!confirm(t('capability_delete_confirm'))) return;
    
    await fetch(`/api/capabilities/${id}`, { method: 'DELETE' });
    loadCapabilities();
}

// Initialize language and load capabilities
(async () => {
    await initLanguageSwitcher();
    
    // Get parent app information to check if it's MCP type and get base URL
    try {
        const appResponse = await fetch(`/api/apps/${serviceId}`);
        const app = await appResponse.json();
        isMcpType = app.service_type === 'mcp';
        baseUrl = app.mcp_url || '';
        
        // Hide "New Capability" button for MCP type
        if (isMcpType) {
            const newCapabilityBtn = document.querySelector('a[href*="/capabilities/new"]');
            if (newCapabilityBtn) {
                newCapabilityBtn.style.display = 'none';
            }
        }
    } catch (e) {
        console.error('Failed to fetch app info:', e);
    }
    
    loadCapabilities();
})();
