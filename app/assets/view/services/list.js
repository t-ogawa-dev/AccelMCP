/**
 * サービス一覧画面
 */

async function loadServices() {
    const response = await fetch('/api/services');
    const services = await response.json();
    
    const container = document.getElementById('services-list');
    
    if (services.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('service_empty')}</div>`;
        return;
    }
    
    container.innerHTML = services.map(service => `
        <div class="list-item">
            <div class="list-item-main">
                <h3><a href="/services/${service.id}">${service.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge">${t('service_subdomain')}: ${service.subdomain}</span>
                    <span class="text-muted">${t('service_registered')}: ${new Date(service.created_at).toLocaleDateString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</span>
                </div>
                ${service.description ? `<p class="text-muted">${service.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <a href="/services/${service.id}/capabilities" class="btn btn-sm">${t('service_capabilities_button')}</a>
                <a href="/services/${service.id}/edit" class="btn btn-sm">${t('button_edit')}</a>
                <button onclick="deleteService(${service.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>
            </div>
        </div>
    `).join('');
}

async function deleteService(id) {
    if (!confirm(t('service_delete_confirm'))) return;
    
    await fetch(`/api/services/${id}`, { method: 'DELETE' });
    loadServices();
}

// 言語初期化完了後にサービス一覧を読み込む
(async () => {
    await initLanguageSwitcher();
    loadServices();
})();
