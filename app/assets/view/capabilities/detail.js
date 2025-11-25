// capabilities/detail.js - Capability Detail Page
const capabilityId = parseInt(window.location.pathname.split('/')[2]);

async function loadCapability() {
    const response = await fetch(`/api/capabilities/${capabilityId}`);
    const cap = await response.json();
    
    // Update breadcrumb links
    // Set breadcrumb links
    const mcpServiceId = cap.mcp_service_id || 1; // APIから取得するか、デフォルト値
    document.getElementById('mcp-service-link').href = `/mcp-services/${mcpServiceId}`;
    document.getElementById('apps-link').href = `/mcp-services/${mcpServiceId}/apps`;
    document.getElementById('service-link').href = `/mcp-services/${mcpServiceId}/apps/${cap.service_id}`;
    document.getElementById('capabilities-link').href = `/mcp-services/${mcpServiceId}/apps/${cap.service_id}/capabilities`;
    document.getElementById('edit-link').href = `/capabilities/${capabilityId}/edit`;
    
    const container = document.getElementById('capability-detail');
    container.innerHTML = `
        <div class="detail-section">
            <h2>${cap.name}</h2>
            <span class="badge badge-${cap.capability_type}">${cap.capability_type.toUpperCase()}</span>
            ${cap.description ? `<p class="text-muted">${cap.description}</p>` : ''}
        </div>
        
        <div class="detail-section">
            <h3>${t("capability_basic_info")}</h3>
            <table class="detail-table">
                <tr>
                    <th>${t("capability_type_detail")}</th>
                    <td><span class="badge badge-${cap.capability_type}">${cap.capability_type.toUpperCase()}</span></td>
                </tr>
                <tr>
                    <th>${t("capability_method_label")}</th>
                    <td><span class="badge badge-method">${cap.headers['X-HTTP-Method'] || 'POST'}</span></td>
                </tr>
                <tr>
                    <th>${t("capability_url_label")}</th>
                    <td><code>${cap.url || 'N/A'}</code></td>
                </tr>
                <tr>
                    <th>${t("capability_registered_at")}</th>
                    <td>${new Date(cap.created_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
                <tr>
                    <th>${t("capability_updated_at")}</th>
                    <td>${new Date(cap.updated_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
            </table>
        </div>
        
        <div class="detail-section">
            <h3>${t("capability_headers_params")}</h3>
            <pre class="code-block">${JSON.stringify(cap.headers, null, 2)}</pre>
        </div>
        
        <div class="detail-section">
            <h3>${t("capability_body_params_label")}</h3>
            <pre class="code-block">${JSON.stringify(cap.body_params, null, 2)}</pre>
        </div>
    `;
}

// Initialize language and load capability detail
(async () => {
    await initLanguageSwitcher();
    loadCapability();
})();
