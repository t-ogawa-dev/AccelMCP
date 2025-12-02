/**
 * サービス一覧画面
 */

async function loadServices(mcpServiceId) {
    const response = await fetch('/api/apps');
    let services = await response.json();
    
    // MCPサービスIDでフィルタリング
    services = services.filter(s => s.mcp_service_id == mcpServiceId);
    
    const container = document.getElementById('services-list');
    
    if (services.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('app_empty')}</div>`;
        return;
    }
    
    container.innerHTML = services.map(service => `
        <div class="list-item ${!service.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/mcp-services/${mcpServiceId}/apps/${service.id}">${service.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge badge-${service.service_type}">${service.service_type.toUpperCase()}</span>
                    ${!service.is_enabled ? `<span class="status-badge disabled">${t('status_disabled')}</span>` : `<span class="status-badge enabled">${t('status_enabled')}</span>`}
                    ${(service.access_control === 'restricted') ? `<span class="badge badge-access-restricted">${t('access_control_restricted')}</span>` : `<span class="badge badge-access-public">${t('access_control_public')}</span>`}
                    <span class="text-muted">${t('app_registered')}: ${new Date(service.created_at).toLocaleDateString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</span>
                </div>
                ${service.description ? `<p class="text-muted">${service.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <label class="toggle-switch">
                    <input type="checkbox" ${service.is_enabled ? 'checked' : ''} onchange="toggleApp(${service.id}, ${mcpServiceId})">
                    <span class="toggle-slider"></span>
                </label>
                <a href="/mcp-services/${mcpServiceId}/apps/${service.id}/capabilities" class="btn btn-sm">${t('app_capabilities_button')}</a>
                <a href="/mcp-services/${mcpServiceId}/apps/${service.id}/edit" class="btn btn-sm">${t('button_edit')}</a>
                <button onclick="deleteService(${service.id}, ${mcpServiceId})" class="btn btn-sm btn-danger">${t('button_delete')}</button>
            </div>
        </div>
    `).join('');
}

async function toggleApp(id, mcpServiceId) {
    try {
        const response = await fetch(`/api/apps/${id}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadServices(mcpServiceId);
        } else {
            const error = await response.json();
            alert('切り替えに失敗しました: ' + (error.error || 'Unknown error'));
        }
    } catch (e) {
        alert('切り替えに失敗しました: ' + e.message);
    }
}

async function deleteService(id, mcpServiceId) {
    if (!confirm(t('app_delete_confirm'))) return;
    
    await fetch(`/api/apps/${id}`, { method: 'DELETE' });
    loadServices(mcpServiceId);
}

// 言語初期化完了後にサービス一覧を読み込む
(async () => {
    await initLanguageSwitcher();
    
    // URLからMCPサービスIDを取得
    const pathParts = window.location.pathname.split('/');
    const mcpServiceId = pathParts[2]; // /mcp-services/{id}/apps
    
    if (!mcpServiceId) {
        console.error('MCP Service ID not found in URL');
        return;
    }
    
    try {
        const response = await fetch(`/api/mcp-services/${mcpServiceId}`);
        const mcpService = await response.json();
        
        // パンくずリストを更新
        const breadcrumb = document.getElementById('breadcrumb');
        breadcrumb.innerHTML = `
            <a href="/dashboard" data-i18n="breadcrumb_home">${t('breadcrumb_home')}</a>
            <span class="breadcrumb-separator">›</span>
            <a href="/mcp-services" data-i18n="mcp_service_list_title">${t('mcp_service_list_title')}</a>
            <span class="breadcrumb-separator">›</span>
            <a href="/mcp-services/${mcpServiceId}">${mcpService.name}</a>
            <span class="breadcrumb-separator">›</span>
            <span class="breadcrumb-current" data-i18n="breadcrumb_app_list">${t('breadcrumb_app_list')}</span>
        `;
        
        // タイトルを更新
        document.getElementById('page-title').textContent = `${mcpService.name} - ${t('app_list_title')}`;
        document.getElementById('page-desc').textContent = mcpService.description || t('app_list_desc');
        
        // 新規作成ボタンにMCPサービスIDを追加
        const newButton = document.getElementById('new-app-button');
        newButton.href = `/mcp-services/${mcpServiceId}/apps/new`;
    } catch (e) {
        console.error('Failed to load MCP service:', e);
    }
    
    loadServices(mcpServiceId);
})();
