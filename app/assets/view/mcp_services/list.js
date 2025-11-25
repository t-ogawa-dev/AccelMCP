/**
 * MCPサービス一覧画面
 */

async function loadMcpServices() {
    const response = await fetch('/api/mcp-services');
    const services = await response.json();
    
    const container = document.getElementById('services-list');
    
    if (services.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('mcp_service_empty')}</div>`;
        return;
    }
    
    container.innerHTML = services.map(service => `
        <div class="list-item ${!service.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/mcp-services/${service.id}">${service.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge">${t('mcp_service_subdomain')}: ${service.subdomain}</span>
                    ${!service.is_enabled ? `<span class="status-badge disabled">${t('status_disabled')}</span>` : `<span class="status-badge enabled">${t('status_enabled')}</span>`}
                    <span class="text-muted">${t('mcp_service_apps_count')}: ${service.apps_count || 0}</span>
                </div>
                ${service.description ? `<p class="text-muted">${service.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <label class="toggle-switch">
                    <input type="checkbox" ${service.is_enabled ? 'checked' : ''} onchange="toggleMcpService(${service.id})">
                    <span class="toggle-slider"></span>
                </label>
                <a href="/mcp-services/${service.id}/apps" class="btn btn-sm">${t('mcp_service_apps_button')}</a>
                <a href="/mcp-services/${service.id}/edit" class="btn btn-sm">${t('button_edit')}</a>
                <button onclick="deleteMcpService(${service.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>
            </div>
        </div>
    `).join('');
}

async function toggleMcpService(id) {
    try {
        const response = await fetch(`/api/mcp-services/${id}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadMcpServices();
        } else {
            const error = await response.json();
            alert('切り替えに失敗しました: ' + (error.error || 'Unknown error'));
        }
    } catch (e) {
        alert('切り替えに失敗しました: ' + e.message);
    }
}

async function deleteMcpService(id) {
    if (!confirm(t('mcp_service_delete_confirm'))) return;
    
    await fetch(`/api/mcp-services/${id}`, { method: 'DELETE' });
    loadMcpServices();
}

// 言語初期化完了後にMCPサービス一覧を読み込む
(async () => {
    await initLanguageSwitcher();
    loadMcpServices();
})();
