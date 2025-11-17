// templates/capability_detail.js - Capability Detail Page

let capability = null;
let template = null;

async function loadCapability() {
    try {
        // Load template first
        const templateResponse = await fetch(`/api/mcp-templates/${TEMPLATE_ID}`);
        template = await templateResponse.json();
        document.getElementById('breadcrumb-template').textContent = template.name;
        
        // Load capability
        const response = await fetch(`/api/template-capabilities/${CAPABILITY_ID}`);
        capability = await response.json();
        
        // Update page
        document.getElementById('capability-name').textContent = capability.name;
        document.getElementById('capability-description').textContent = capability.description || '';
        document.getElementById('breadcrumb-capability').textContent = capability.name;
        
        // Basic info
        document.getElementById('detail-name').textContent = capability.name;
        document.getElementById('detail-type').textContent = capability.capability_type;
        document.getElementById('detail-url').textContent = capability.url || '-';
        
        // Headers
        const headersContainer = document.getElementById('headers-list');
        let headers = {};
        if (capability.headers) {
            headers = typeof capability.headers === 'string' 
                ? JSON.parse(capability.headers) 
                : capability.headers;
        }
        if (Object.keys(headers).length === 0) {
            headersContainer.innerHTML = `<div class="empty-state" data-i18n="capability_no_headers">${t('capability_no_headers')}</div>`;
        } else {
            headersContainer.innerHTML = Object.entries(headers).map(([key, value]) => `
                <div class="header-item">
                    <span class="header-key">${key}</span>
                    <span class="header-value">${value}</span>
                </div>
            `).join('');
        }
        
        // Body params
        const paramsContainer = document.getElementById('body-params-list');
        let params = {};
        if (capability.body_params) {
            params = typeof capability.body_params === 'string' 
                ? JSON.parse(capability.body_params) 
                : capability.body_params;
        }
        if (Object.keys(params).length === 0) {
            paramsContainer.innerHTML = `<div class="empty-state" data-i18n="capability_no_params">${t('capability_no_params')}</div>`;
        } else {
            paramsContainer.innerHTML = Object.entries(params).map(([key, value]) => `
                <div class="param-item">
                    <span class="param-key">${key}</span>
                    <span class="param-value">${JSON.stringify(value)}</span>
                </div>
            `).join('');
        }
        
        // Template content
        const templateSection = document.getElementById('template-section');
        if (capability.template_content) {
            document.getElementById('template-content').textContent = capability.template_content;
        } else {
            templateSection.style.display = 'none';
        }
        
        // Hide edit/delete buttons for builtin templates
        if (template.template_type === 'builtin') {
            document.getElementById('edit-btn').style.display = 'none';
            document.getElementById('delete-btn').style.display = 'none';
        }
        
    } catch (e) {
        alert('Failed to load capability: ' + e.message);
    }
}

async function deleteCapability() {
    if (!confirm(t('capability_delete_confirm'))) return;
    
    try {
        const response = await fetch(`/api/template-capabilities/${CAPABILITY_ID}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            window.location.href = `/templates/${TEMPLATE_ID}/capabilities?message=${encodeURIComponent('削除しました')}`;
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
    await loadCapability();
})();
