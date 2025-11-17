// services/detail.js - Service Detail Page
const serviceId = parseInt(window.location.pathname.split('/')[2]);

async function loadService() {
    const response = await fetch(`/api/services/${serviceId}`);
    const service = await response.json();
    
    const container = document.getElementById('service-detail');
    container.innerHTML = `
        <div class="detail-section">
            <h2>${service.name}</h2>
            ${service.description ? `<p class="text-muted">${service.description}</p>` : ''}
        </div>
        
        <div class="detail-section">
            <h3>${t('service_basic_info')}</h3>
            <table class="detail-table">
                <tr>
                    <th>${t('service_subdomain_label')}</th>
                    <td><code>${service.subdomain}</code></td>
                </tr>
                <tr>
                    <th>${t('service_mcp_endpoint')}</th>
                    <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <code id="mcp-endpoint">http://${service.subdomain}.lvh.me:5001/mcp</code>
                            <button onclick="copyEndpoint(this)" class="btn btn-secondary" style="padding: 4px 12px; font-size: 13px;" data-i18n="button_copy">${t('button_copy')}</button>
                        </div>
                    </td>
                </tr>
                <tr>
                    <th>${t('service_registered_at')}</th>
                    <td>${new Date(service.created_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
                <tr>
                    <th>${t('service_updated_at')}</th>
                    <td>${new Date(service.updated_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
            </table>
        </div>
        
        <div class="detail-section">
            <h3>${t('service_common_headers')}</h3>
            <pre class="code-block">${JSON.stringify(service.common_headers, null, 2)}</pre>
        </div>
    `;
}

function copyEndpoint(button) {
    const endpointElement = document.getElementById('mcp-endpoint');
    const endpoint = endpointElement.textContent;
    
    // Try modern Clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(endpoint).then(() => {
            showCopySuccess(button);
        }).catch(err => {
            // Fallback to older method
            fallbackCopy(endpoint, button);
        });
    } else {
        // Use fallback method
        fallbackCopy(endpoint, button);
    }
}

function fallbackCopy(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopySuccess(button);
    } catch (err) {
        console.error('Failed to copy:', err);
        alert(currentLanguage === 'ja' ? 'コピーに失敗しました' : 'Failed to copy');
    } finally {
        document.body.removeChild(textArea);
    }
}

function showCopySuccess(button) {
    // Show success message
    const originalText = button.textContent;
    button.textContent = currentLanguage === 'ja' ? 'コピーしました！' : 'Copied!';
    button.style.background = '#28a745';
    
    setTimeout(() => {
        button.textContent = originalText;
        button.style.background = '';
    }, 2000);
}

// Initialize language and load service detail
(async () => {
    await initLanguageSwitcher();
    loadService();
})();
