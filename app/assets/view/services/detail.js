// services/detail.js - Service Detail Page
const pathParts = window.location.pathname.split('/');
const mcpServiceId = parseInt(pathParts[2]);
const serviceId = parseInt(pathParts[4]);

async function loadService() {
    const response = await fetch(`/api/apps/${serviceId}`);
    const service = await response.json();
    
    const isMcpType = service.service_type === 'mcp';
    
    // Build endpoint URL row (show for both MCP and API types)
    let endpointRow = '';
    if (service.mcp_url) {
        const urlLabel = isMcpType ? t('app_endpoint_url') : 'ベースURL';
        endpointRow = `
                <tr>
                    <th>${urlLabel}</th>
                    <td><code>${service.mcp_url}</code></td>
                </tr>`;
    }
    
    const container = document.getElementById('service-detail');
    container.innerHTML = `
        <div class="detail-section">
            <h2>${service.name}</h2>
            ${service.description ? `<p class="text-muted">${service.description}</p>` : ''}
        </div>
        
        <div class="detail-section">
            <h3>${t('app_basic_info')}</h3>
            <table class="detail-table">
                <tr>
                    <th>${t('app_type_label')}</th>
                    <td><span class="badge badge-${service.service_type}">${service.service_type.toUpperCase()}</span></td>
                </tr>${endpointRow}
                <tr>
                    <th>${t('access_control')}</th>
                    <td>
                        <span id="access-control-badge"></span>
                    </td>
                </tr>
                <tr>
                    <th>${t('app_registered_at')}</th>
                    <td>${new Date(service.created_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
                <tr>
                    <th>${t('app_updated_at')}</th>
                    <td>${new Date(service.updated_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
            </table>
        </div>
        
        <div class="detail-section">
            <h3>${t('app_common_headers')}</h3>
            <pre class="code-block">${JSON.stringify(service.common_headers, null, 2)}</pre>
        </div>
    `;
    
    // Update access control UI
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

// Initialize language and load service detail
(async () => {
    await initLanguageSwitcher();
    loadService();
})();

