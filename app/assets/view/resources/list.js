/**
 * Resources一覧画面
 */

function toggleAccordion() {
    const content = document.getElementById('usage-accordion');
    const icon = document.querySelector('.accordion-icon');
    
    if (content.style.maxHeight) {
        content.style.maxHeight = null;
        icon.classList.remove('rotate');
    } else {
        content.style.maxHeight = content.scrollHeight + 'px';
        icon.classList.add('rotate');
    }
}

async function loadResources() {
    const response = await fetch('/api/resources');
    const resources = await response.json();
    
    const container = document.getElementById('resources-list');
    
    if (resources.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('resource_empty')}</div>`;
        return;
    }
    
    container.innerHTML = resources.map(resource => {
        const statusBadge = resource.is_enabled
            ? `<span class="status-badge enabled">${t('status_enabled')}</span>`
            : `<span class="status-badge disabled">${t('status_disabled')}</span>`;
        
        // Usage count badge
        const usageCount = resource.usage_count || 0;
        const usageBadge = usageCount > 0
            ? `<span class="badge" style="background: #fef3c7; color: #92400e; margin-left: 8px;">📊 ${usageCount}個のCapabilityで使用中</span>`
            : '';
        
        // Disable delete button if resource is in use
        const isInUse = usageCount > 0;
        
        return `
        <div class="list-item ${!resource.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/resources/${resource.id}">${resource.name}</a></h3>
                <div class="list-item-meta">
                    ${statusBadge}
                    <span class="badge badge-mime">${resource.mime_type}</span>
                    ${usageBadge}
                </div>
                <p class="text-muted" style="font-size: 12px; margin-top: 5px;">URI: <code>${resource.uri}</code></p>
                ${resource.description ? `<p class="text-muted">${resource.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <label class="toggle-switch">
                    <input type="checkbox" ${resource.is_enabled ? 'checked' : ''} onchange="toggleResource(${resource.id})">
                    <span class="toggle-slider"></span>
                </label>
                <a href="/resources/${resource.id}/edit" class="btn btn-sm btn-secondary">${t('button_edit')}</a>
                <button onclick="${isInUse ? 'return false;' : `deleteResource(${resource.id})`}" class="btn btn-sm btn-danger" ${isInUse ? 'disabled="disabled"' : ''} ${isInUse ? 'title="このResourceは使用中のため削除できません"' : ''}>${t('button_delete')}</button>
            </div>
        </div>
    `;
    }).join('');
}

async function toggleResource(id) {
    try {
        const response = await fetch(`/api/resources/${id}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadResources();
        } else {
            const error = await response.json();
            await modal.error(t('common_error') + ': ' + (error.error || t('error_unknown')));
        }
    } catch (e) {
        await modal.error(t('common_error') + ': ' + e.message);
    }
}

async function deleteResource(id) {
    const confirmed = await modal.confirmDelete(t('resource_delete_confirm'));
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/api/resources/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadResources();
        } else {
            const error = await response.json();
            await modal.error(t('common_error') + ': ' + (error.error || t('error_unknown')));
        }
    } catch (e) {
        await modal.error(t('common_error') + ': ' + e.message);
    }
}

// 言語初期化完了後にResources一覧を読み込む
(async () => {
    await initLanguageSwitcher();
    loadResources();
})();
