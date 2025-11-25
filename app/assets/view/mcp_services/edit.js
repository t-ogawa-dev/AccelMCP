/**
 * MCPサービス編集画面
 */

const mcpServiceId = parseInt(window.location.pathname.split('/')[2]);

async function loadMcpService() {
    const response = await fetch(`/api/mcp-services/${mcpServiceId}`);
    const service = await response.json();
    
    document.getElementById('name').value = service.name;
    document.getElementById('subdomain').value = service.subdomain;
    document.getElementById('description').value = service.description || '';
}

(async () => {
    await initLanguageSwitcher();
    await loadMcpService();
    
    document.getElementById('mcp-service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            subdomain: formData.get('subdomain'),
            description: formData.get('description')
        };
        
        const response = await fetch(`/api/mcp-services/${mcpServiceId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = `/mcp-services/${mcpServiceId}`;
        } else {
            const error = await response.json();
            alert(t('mcp_service_update_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
