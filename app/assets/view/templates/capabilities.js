// templates/capabilities.js - Template Capabilities Management Page

let template = null;
let isBuiltin = false;

function showFlashMessage(message) {
    const flashDiv = document.getElementById('flash-message');
    flashDiv.textContent = message;
    flashDiv.style.display = 'block';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        flashDiv.style.display = 'none';
    }, 5000);
}

async function loadTemplate() {
    try {
        const response = await fetch(`/api/mcp-templates/${TEMPLATE_ID}`);
        template = await response.json();
        
        document.getElementById('breadcrumb-template').textContent = template.name;
        document.getElementById('page-title').textContent = `${template.name} - Capabilities`;
        
        isBuiltin = template.template_type === 'builtin';
        
        // Hide new button for builtin templates
        if (isBuiltin) {
            document.getElementById('new-btn').style.display = 'none';
            
            // Show notice
            const notice = document.createElement('div');
            notice.className = 'builtin-notice';
            notice.textContent = '標準搭載テンプレートのCapabilitiesは編集できません。閲覧のみ可能です。';
            document.querySelector('.capabilities-container').insertBefore(
                notice,
                document.getElementById('capabilities-list')
            );
        }
        
        await loadCapabilities();
        
    } catch (e) {
        alert('Failed to load template: ' + e.message);
    }
}

async function loadCapabilities() {
    const container = document.getElementById('capabilities-list');
    
    if (!template.capabilities || template.capabilities.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p data-i18n="capability_empty">${t('capability_empty')}</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = template.capabilities.map(cap => `
        <div class="capability-card" onclick="viewCapability(${cap.id})">
            <div class="capability-header">
                <div class="capability-info">
                    <div class="capability-name">${cap.name}</div>
                    <span class="capability-type ${cap.capability_type}">${cap.capability_type}</span>
                </div>
                <div class="capability-actions">
                    ${!isBuiltin ? `<button class="btn-small btn-secondary" onclick="editCapability(${cap.id}, event)" data-i18n="button_edit">${t('button_edit')}</button>` : ''}
                    ${!isBuiltin ? `<button class="btn-small btn-delete" onclick="deleteCapability(${cap.id}, event)" data-i18n="button_delete">${t('button_delete')}</button>` : ''}
                </div>
            </div>
            ${cap.url ? `<div class="capability-url">${cap.url}</div>` : ''}
            ${cap.description ? `<div class="capability-description">${cap.description}</div>` : ''}
        </div>
    `).join('');
}

function viewCapability(capabilityId) {
    window.location.href = `/mcp-templates/${TEMPLATE_ID}/capabilities/${capabilityId}`;
}

function editCapability(capabilityId, event) {
    event.stopPropagation();
    window.location.href = `/mcp-templates/${TEMPLATE_ID}/capabilities/${capabilityId}/edit`;
}

async function deleteCapability(capabilityId, event) {
    event.stopPropagation();
    
    if (!confirm(t('capability_delete_confirm'))) return;
    
    try {
        const response = await fetch(`/api/template-capabilities/${capabilityId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showFlashMessage('削除しました');
            // Reload template data
            await loadTemplate();
        } else {
            const error = await response.json();
            alert('削除に失敗しました: ' + (error.error || 'Unknown error'));
        }
    } catch (e) {
        alert('削除に失敗しました: ' + e.message);
    }
}

// Initialize
(async () => {
    await initLanguageSwitcher();
    await loadTemplate();
    
    // Check for flash message in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    if (message) {
        showFlashMessage(decodeURIComponent(message));
        // Remove message from URL
        window.history.replaceState({}, '', `/mcp-templates/${TEMPLATE_ID}/capabilities`);
    }
})();
