// templates/detail.js - Template Detail Page

let template = null;

async function loadTemplate() {
    try {
        const response = await fetch(`/api/mcp-templates/${TEMPLATE_ID}`);
        template = await response.json();
        
        // Update page
        document.getElementById('template-name').textContent = `${template.icon || '📦'} ${template.name}`;
        document.getElementById('template-description').textContent = template.description || '';
        document.getElementById('breadcrumb-name').textContent = template.name;
        
        // Basic info
        document.getElementById('detail-name').textContent = template.name;
        document.getElementById('detail-service-type').textContent = template.service_type.toUpperCase();
        document.getElementById('detail-category').textContent = template.category || '-';
        document.getElementById('detail-icon').textContent = template.icon || '-';
        
        // MCP URL
        if (template.mcp_url) {
            document.getElementById('mcp-url-item').style.display = 'flex';
            const mcpUrlElement = document.getElementById('detail-mcp-url');
            mcpUrlElement.innerHTML = `<a href="${template.mcp_url}" target="_blank">${template.mcp_url}</a>`;
        }
        
        // Official URL
        if (template.official_url) {
            document.getElementById('official-url-item').style.display = 'flex';
            const officialUrlElement = document.getElementById('detail-official-url');
            officialUrlElement.innerHTML = `<a href="${template.official_url}" target="_blank">${template.official_url}</a>`;
        }
        
        // Headers
        const headersContainer = document.getElementById('headers-list');
        let headers = {};
        if (template.common_headers) {
            // Check if it's already an object or needs parsing
            headers = typeof template.common_headers === 'string' 
                ? JSON.parse(template.common_headers) 
                : template.common_headers;
        }
        if (Object.keys(headers).length === 0) {
            headersContainer.innerHTML = '<div class="empty-state">共通ヘッダーが設定されていません</div>';
        } else {
            headersContainer.innerHTML = Object.entries(headers).map(([key, value]) => `
                <div class="header-item">
                    <span class="header-key">${key}</span>
                    <span class="header-value">${value}</span>
                </div>
            `).join('');
        }
        
        // Hide edit/delete/export buttons for builtin templates
        if (template.template_type === 'builtin') {
            document.getElementById('edit-btn').style.display = 'none';
            document.getElementById('delete-btn').style.display = 'none';
            document.getElementById('export-btn').style.display = 'none';
        }
        
    } catch (e) {
        alert('Failed to load template: ' + e.message);
    }
}

async function exportTemplate() {
    try {
        const response = await fetch(`/api/mcp-templates/${TEMPLATE_ID}/export`);
        const data = await response.json();
        
        // Download as JSON file
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export-template-${data.name}.json`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        alert('Export failed: ' + e.message);
    }
}

async function deleteTemplate() {
    if (!confirm(t('mcp_template_delete_confirm'))) return;
    
    try {
        const response = await fetch(`/api/mcp-templates/${TEMPLATE_ID}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('テンプレートを削除しました');
            window.location.href = '/mcp-templates';
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
})();
