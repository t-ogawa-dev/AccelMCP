/**
 * MCPサービス詳細画面
 * v1.1 - アクセス制御表示追加
 */

const mcpServiceId = parseInt(window.location.pathname.split('/')[2]);

async function copyEndpoint(btn) {
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
            await modal.error(errorMsg);
        }
    } catch (err) {
        console.error('Failed to copy:', err);
        const errorMsg = currentLanguage === 'ja' ? 'コピーに失敗しました: ' : 'Failed to copy: ';
        await modal.error(errorMsg + err.message);
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
        await modal.success(successMsg);
    } catch (error) {
        console.error('Export failed:', error);
        const errorMsg = currentLanguage === 'ja' ? 'エクスポートに失敗しました' : 'Export failed';
        await modal.error(errorMsg);
    }
}

async function loadMcpService() {
    const response = await fetch(`/api/mcp-services/${mcpServiceId}`);
    const service = await response.json();
    
    // Update breadcrumb with service name
    const breadcrumbCurrent = document.querySelector('.breadcrumb-current');
    if (breadcrumbCurrent && service.name) {
        breadcrumbCurrent.textContent = service.name;
    }
    
    // Basic info
    document.getElementById('service-name').textContent = service.name;
    document.getElementById('name').textContent = service.name;
    document.getElementById('identifier').textContent = service.identifier;
    
    // Generate endpoint based on routing type
    const currentHost = window.location.host;
    const protocol = window.location.protocol;
    
    let endpoint;
    if (service.routing_type === 'path') {
        endpoint = `${protocol}//${currentHost}/${service.identifier}/mcp`;
    } else {
        // For subdomain routing
        const hostWithoutPort = currentHost.split(':')[0];
        const port = currentHost.includes(':') ? ':' + currentHost.split(':')[1] : '';
        const hostParts = hostWithoutPort.split('.');
        
        let subdomainHost;
        if (hostParts.length >= 4 || (hostParts.length === 3 && !['com', 'net', 'org', 'io', 'dev', 'app'].includes(hostParts[hostParts.length-1]))) {
            // Has subdomain: replace first part
            hostParts[0] = service.identifier;
            subdomainHost = hostParts.join('.') + port;
        } else if (hostParts.length === 3) {
            // 3 parts with common TLD: replace first
            hostParts[0] = service.identifier;
            subdomainHost = hostParts.join('.') + port;
        } else {
            // 2 or less parts: add prefix
            subdomainHost = `${service.identifier}.${currentHost}`;
        }
        endpoint = `${protocol}//${subdomainHost}/mcp`;
    }
    document.getElementById('mcp-endpoint').textContent = endpoint;
    
    document.getElementById('description').textContent = service.description || '-';
    
    // Access control
    const badge = document.getElementById('access-control-badge');
    const isPublic = service.access_control === 'public';
    
    if (isPublic) {
        badge.textContent = t('access_control_public');
        badge.style.cssText = 'padding: 4px 12px; border-radius: 4px; background-color: #d1fae5; color: #065f46; font-weight: 500; font-size: 0.875rem;';
    } else {
        badge.textContent = t('access_control_restricted');
        badge.style.cssText = 'padding: 4px 12px; border-radius: 4px; background-color: #fef3c7; color: #92400e; font-weight: 500; font-size: 0.875rem;';
    }
}

(async () => {
    await initLanguageSwitcher();
    loadMcpService();
})();
