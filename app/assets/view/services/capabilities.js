// services/capabilities.js - Service Capabilities List
const pathParts = window.location.pathname.split('/');
const mcpServiceId = parseInt(pathParts[2]);
const serviceId = parseInt(pathParts[4]);
let isMcpType = false;

async function loadCapabilities() {
    const response = await fetch(`/api/apps/${serviceId}/capabilities`);
    const capabilities = await response.json();
    
    const container = document.getElementById('capabilities-list');
    
    if (capabilities.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('capability_empty')}</div>`;
        return;
    }
    
    container.innerHTML = capabilities.map(cap => `
        <div class="list-item ${!cap.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/capabilities/${cap.id}">${cap.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge badge-${cap.capability_type}">${cap.capability_type.toUpperCase()}</span>
                    ${!cap.is_enabled ? `<span class="status-badge disabled">${t('status_disabled')}</span>` : `<span class="status-badge enabled">${t('status_enabled')}</span>`}
                    <span class="text-muted">${cap.url || 'N/A'}</span>
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
    `).join('');
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
    
    // Get parent app information to check if it's MCP type
    try {
        const appResponse = await fetch(`/api/apps/${serviceId}`);
        const app = await appResponse.json();
        isMcpType = app.service_type === 'mcp';
        
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
