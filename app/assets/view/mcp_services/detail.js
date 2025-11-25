/**
 * MCPサービス詳細画面
 */

const mcpServiceId = parseInt(window.location.pathname.split('/')[2]);

function copyEndpoint(btn) {
    const endpoint = document.getElementById('mcp-endpoint').textContent;
    
    // Create temporary textarea element
    const textarea = document.createElement('textarea');
    textarea.value = endpoint;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    
    try {
        textarea.select();
        textarea.setSelectionRange(0, 99999); // For mobile devices
        
        const successful = document.execCommand('copy');
        
        if (successful) {
            // Show success feedback
            const originalText = btn.innerHTML;
            const copiedText = currentLanguage === 'ja' ? '✓ コピーしました' : '✓ Copied';
            btn.innerHTML = '<span>' + copiedText + '</span>';
            btn.style.backgroundColor = '#10b981';
            btn.style.borderColor = '#10b981';
            btn.style.color = 'white';
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.backgroundColor = '';
                btn.style.borderColor = '';
                btn.style.color = '';
            }, 2000);
        } else {
            const errorMsg = currentLanguage === 'ja' ? 'コピーに失敗しました' : 'Failed to copy';
            alert(errorMsg);
        }
    } catch (err) {
        console.error('Failed to copy:', err);
        const errorMsg = currentLanguage === 'ja' ? 'コピーに失敗しました: ' : 'Failed to copy: ';
        alert(errorMsg + err.message);
    } finally {
        document.body.removeChild(textarea);
    }
}

async function exportMcpService() {
    try {
        const response = await fetch(`/api/mcp-services/${mcpServiceId}/export`);
        if (!response.ok) throw new Error('Export failed');
        
        const data = await response.json();
        
        // Download as JSON file
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${data.name}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Show success message
        const successMsg = currentLanguage === 'ja' ? 'エクスポートしました' : 'Exported successfully';
        alert(successMsg);
    } catch (error) {
        console.error('Export failed:', error);
        const errorMsg = currentLanguage === 'ja' ? 'エクスポートに失敗しました' : 'Export failed';
        alert(errorMsg);
    }
}

async function loadMcpService() {
    const response = await fetch(`/api/mcp-services/${mcpServiceId}`);
    const service = await response.json();
    
    // Basic info
    document.getElementById('service-name').textContent = service.name;
    document.getElementById('name').textContent = service.name;
    document.getElementById('subdomain').textContent = service.subdomain;
    document.getElementById('mcp-endpoint').textContent = `http://${service.subdomain}.lvh.me:5001/mcp`;
    document.getElementById('description').textContent = service.description || '-';
    
    // Apps list
    const appsContainer = document.getElementById('apps-list');
    
    if (!service.apps || service.apps.length === 0) {
        appsContainer.innerHTML = `<div class="empty-state">${t('app_empty')}</div>`;
        return;
    }
    
    appsContainer.innerHTML = service.apps.map(app => `
        <div class="list-item ${!app.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/mcp-services/${service.id}/apps/${app.id}">${app.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge badge-${app.service_type}">${app.service_type.toUpperCase()}</span>
                    ${!app.is_enabled ? `<span class="status-badge disabled">${t('status_disabled')}</span>` : `<span class="status-badge enabled">${t('status_enabled')}</span>`}
                </div>
                ${app.description ? `<p class="text-muted">${app.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <a href="/mcp-services/${service.id}/apps/${app.id}/capabilities" class="btn btn-sm">${t('app_capabilities_button')}</a>
                <a href="/mcp-services/${service.id}/apps/${app.id}/edit" class="btn btn-sm">${t('button_edit')}</a>
            </div>
        </div>
    `).join('');
}

(async () => {
    await initLanguageSwitcher();
    loadMcpService();
})();
