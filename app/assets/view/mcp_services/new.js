/**
 * MCPサービス新規登録画面
 */

function updateRoutingHint() {
    const routingType = document.getElementById('routing_type').value;
    const identifier = document.getElementById('identifier').value || '{identifier}';
    const hintElement = document.getElementById('routing-hint');
    
    // Get current host from window.location
    const currentHost = window.location.host; // includes port if present
    const protocol = window.location.protocol; // http: or https:
    
    if (routingType === 'path') {
        hintElement.innerHTML = `<span data-i18n="mcp_service_routing_hint_path">パス方式: ${protocol}//${currentHost}/${identifier}/mcp</span>`;
    } else {
        // For subdomain routing
        const hostWithoutPort = currentHost.split(':')[0];
        const port = currentHost.includes(':') ? ':' + currentHost.split(':')[1] : '';
        const hostParts = hostWithoutPort.split('.');
        
        let subdomainHost;
        // Check if it's a multi-level TLD or already has subdomain
        // Examples: auc.co.jp (2+1), www.auc.co.jp (1+2+1), auc-mcp.ngrok.io (1+2)
        if (hostParts.length >= 4 || (hostParts.length === 3 && !['com', 'net', 'org', 'io', 'dev', 'app'].includes(hostParts[hostParts.length-1]))) {
            // Has subdomain: replace first part (e.g., www.auc.co.jp -> sample.auc.co.jp)
            hostParts[0] = identifier;
            subdomainHost = hostParts.join('.') + port;
        } else if (hostParts.length === 3) {
            // 3 parts with common TLD: replace first (e.g., auc-mcp.ngrok.io -> sample.ngrok.io)
            hostParts[0] = identifier;
            subdomainHost = hostParts.join('.') + port;
        } else {
            // 2 or less parts: add prefix (e.g., auc.com -> sample.auc.com)
            subdomainHost = `${identifier}.${currentHost}`;
        }
        hintElement.innerHTML = `<span data-i18n="mcp_service_routing_hint_subdomain">サブドメイン方式: ${protocol}//${subdomainHost}/mcp</span>`;
    }
}

(async () => {
    await initLanguageSwitcher();
    
    // Routing type change handler
    document.getElementById('routing_type').addEventListener('change', updateRoutingHint);
    document.getElementById('identifier').addEventListener('input', updateRoutingHint);
    
    document.getElementById('mcp-service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            identifier: formData.get('identifier'),
            routing_type: formData.get('routing_type'),
            description: formData.get('description')
        };
        
        const response = await fetch('/api/mcp-services', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = '/mcp-services';
        } else {
            const error = await response.json();
            await modal.error(t('mcp_service_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
