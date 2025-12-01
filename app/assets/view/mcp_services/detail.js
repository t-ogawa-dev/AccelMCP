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
    document.getElementById('mcp-endpoint').textContent = `http://${service.subdomain}.lvh.me:5000/mcp`;
    document.getElementById('description').textContent = service.description || '-';
}

(async () => {
    await initLanguageSwitcher();
    loadMcpService();
})();
