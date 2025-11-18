/**
 * サービス一覧画面
 */

async function loadServices() {
    const response = await fetch('/api/apps');
    const services = await response.json();
    
    const container = document.getElementById('services-list');
    
    if (services.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('app_empty')}</div>`;
        return;
    }
    
    container.innerHTML = services.map(service => `
        <div class="list-item ${!service.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/services/${service.id}">${service.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge">${t('app_subdomain')}: ${service.subdomain}</span>
                    ${!service.is_enabled ? `<span class="status-badge disabled">${t('status_disabled')}</span>` : `<span class="status-badge enabled">${t('status_enabled')}</span>`}
                    <span class="text-muted">${t('app_registered')}: ${new Date(service.created_at).toLocaleDateString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</span>
                </div>
                ${service.description ? `<p class="text-muted">${service.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <label class="toggle-switch">
                    <input type="checkbox" ${service.is_enabled ? 'checked' : ''} onchange="toggleApp(${service.id})">
                    <span class="toggle-slider"></span>
                </label>
                <a href="/services/${service.id}/capabilities" class="btn btn-sm">${t('app_capabilities_button')}</a>
                <a href="/services/${service.id}/edit" class="btn btn-sm">${t('button_edit')}</a>
                <button onclick="deleteService(${service.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>
            </div>
        </div>
    `).join('');
}

async function toggleApp(id) {
    try {
        const response = await fetch(`/api/apps/${id}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadServices();
        } else {
            const error = await response.json();
            alert('切り替えに失敗しました: ' + (error.error || 'Unknown error'));
        }
    } catch (e) {
        alert('切り替えに失敗しました: ' + e.message);
    }
}

async function deleteService(id) {
    if (!confirm(t('app_delete_confirm'))) return;
    
    await fetch(`/api/apps/${id}`, { method: 'DELETE' });
    loadServices();
}

// 言語初期化完了後にサービス一覧を読み込む
(async () => {
    await initLanguageSwitcher();
    loadServices();
})();
