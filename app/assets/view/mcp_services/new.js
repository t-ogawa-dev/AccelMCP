/**
 * MCPサービス新規登録画面
 */

(async () => {
    await initLanguageSwitcher();
    
    document.getElementById('mcp-service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            subdomain: formData.get('subdomain'),
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
            alert(t('mcp_service_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
