// capabilities/detail.js - Capability Detail Page
const capabilityId = parseInt(window.location.pathname.split('/')[2]);

async function loadCapability() {
    const response = await fetch(`/api/capabilities/${capabilityId}`);
    const cap = await response.json();
    
    let baseUrl = '';
    let serviceType = 'api'; // default
    
    // Update breadcrumb links and fetch base URL
    if (cap.mcp_service_id && cap.service_id) {
        const mcpServiceId = cap.mcp_service_id;
        const serviceId = cap.service_id;
        
        document.getElementById('mcp-service-link').href = `/mcp-services/${mcpServiceId}`;
        document.getElementById('apps-link').href = `/mcp-services/${mcpServiceId}/apps`;
        document.getElementById('service-link').href = `/mcp-services/${mcpServiceId}/apps/${serviceId}`;
        document.getElementById('capabilities-link').href = `/mcp-services/${mcpServiceId}/apps/${serviceId}/capabilities`;
        
        // Fetch service name, base URL, and service type for breadcrumb
        try {
            const serviceResponse = await fetch(`/api/apps/${serviceId}`);
            const service = await serviceResponse.json();
            if (service.mcp_service_name) {
                document.getElementById('mcp-service-link').textContent = service.mcp_service_name;
            }
            // Set app name in breadcrumb
            document.getElementById('service-link').textContent = service.name;
            
            baseUrl = service.mcp_url || '';
            serviceType = service.service_type || 'api';
        } catch (e) {
            console.error('Failed to fetch service info for breadcrumb:', e);
        }
    }
    
    document.getElementById('edit-link').href = `/capabilities/${capabilityId}/edit`;
    
    // Set capability name in breadcrumb (after cap is loaded)
    const breadcrumbCurrent = document.querySelector('.breadcrumb-current');
    if (breadcrumbCurrent && cap.name) {
        breadcrumbCurrent.textContent = cap.name;
    }
    
    // Build full URL display
    let urlDisplay = cap.url || 'N/A';
    if (baseUrl && cap.url && !cap.url.startsWith('http')) {
        const separator = baseUrl.endsWith('/') || cap.url.startsWith('/') ? '' : '/';
        urlDisplay = `<span style="color: #666;">${baseUrl}</span>${separator}<span style="font-weight: 600;">${cap.url}</span>`;
    }
    
    // Filter out internal headers (X-HTTP-Method)
    const displayHeaders = { ...cap.headers };
    delete displayHeaders['X-HTTP-Method'];
    
    // Parse body_params if it's a string
    let bodyParams = cap.body_params;
    if (typeof bodyParams === 'string') {
        try {
            bodyParams = JSON.parse(bodyParams);
        } catch (e) {
            bodyParams = {};
        }
    }
    
    // Separate body_params into fixed parameters (const) and LLM parameters
    const fixedParams = {};
    const llmParams = { properties: {}, required: [] };
    
    // Handle both old format (direct properties) and new format (properties wrapper)
    const properties = bodyParams.properties || bodyParams;
    
    if (properties && typeof properties === 'object') {
        for (const [key, value] of Object.entries(properties)) {
            if (value && typeof value === 'object') {
                if (value.const !== undefined) {
                    // Fixed parameter (has const constraint)
                    fixedParams[key] = value.const;
                } else {
                    // LLM parameter (no const constraint)
                    llmParams.properties[key] = value;
                    // Add to required array if marked as required
                    if (value.required === true) {
                        llmParams.required.push(key);
                    }
                }
            }
        }
        
        // Also check bodyParams.required array if exists
        if (bodyParams.required && Array.isArray(bodyParams.required)) {
            for (const key of bodyParams.required) {
                if (!fixedParams.hasOwnProperty(key) && !llmParams.required.includes(key)) {
                    llmParams.required.push(key);
                }
            }
        }
    }
    
    // Relay parameters label and description based on service type
    const relayParamsLabel = serviceType === 'mcp' 
        ? t('capability_relay_params_to_mcp')
        : t('capability_relay_params_to_api');
    const relayParamsDescription = serviceType === 'mcp'
        ? t('capability_relay_params_description_mcp')
        : t('capability_relay_params_description_api');
    
    // Build relay params structure showing actual format sent to API/MCP
    const relayParamsDisplay = {};
    
    // Add fixed params first (with actual const values)
    for (const [key, value] of Object.entries(fixedParams)) {
        relayParamsDisplay[key] = value;
    }
    
    // Add LLM params (with type placeholders)
    for (const [key, schema] of Object.entries(llmParams.properties)) {
        // Show type placeholder for LLM-set values
        const typeHint = schema.type ? `<${schema.type}>` : '<value>';
        relayParamsDisplay[key] = typeHint;
    }
    
    console.log('Final relayParamsDisplay:', JSON.stringify(relayParamsDisplay, null, 2));
    
    // Helper function to escape HTML in JSON output
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    const relayParamsJson = Object.keys(relayParamsDisplay).length > 0 
        ? escapeHtml(JSON.stringify(relayParamsDisplay, null, 2))
        : t('capability_no_relay_params');
    const llmParamsJson = Object.keys(llmParams.properties).length > 0 
        ? escapeHtml(JSON.stringify(llmParams, null, 2))
        : t('capability_no_params');
    
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
                    <th>${t('access_control')}</th>
                    <td>
                        <span id="access-control-badge"></span>
                    </td>
                </tr>
                <tr>
                    <th>${t("capability_method_label")}</th>
                    <td><span class="badge badge-method">${cap.headers['X-HTTP-Method'] || 'POST'}</span></td>
                </tr>
                <tr>
                    <th>${t("capability_url_label")}</th>
                    <td><code style="font-size: 0.9em;">${urlDisplay}</code></td>
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
            <h3>${t("capability_individual_headers")}</h3>
            <pre class="code-block">${Object.keys(displayHeaders).length > 0 ? JSON.stringify(displayHeaders, null, 2) : t('capability_no_headers')}</pre>
        </div>
        
        <div class="detail-section">
            <h3>${relayParamsLabel}</h3>
            <p class="text-muted" style="font-size: 0.9em; margin-bottom: 0.5rem;">${relayParamsDescription}</p>
            <pre class="code-block">${relayParamsJson}</pre>
        </div>
        
        <div class="detail-section">
            <h3>${t("capability_body_params_label")}</h3>
            <p class="text-muted" style="font-size: 0.9em; margin-bottom: 0.5rem;">${t('capability_llm_params_description')}</p>
            <pre class="code-block">${llmParamsJson}</pre>
        </div>
    `;
    
    // Update access control badge
    const badge = document.getElementById('access-control-badge');
    const isPublic = cap.access_control === 'public';
    
    if (isPublic) {
        badge.textContent = t('access_control_public');
        badge.style.cssText = 'padding: 4px 12px; border-radius: 4px; background-color: #d1fae5; color: #065f46; font-weight: 500; font-size: 0.875rem;';
    } else {
        badge.textContent = t('access_control_restricted');
        badge.style.cssText = 'padding: 4px 12px; border-radius: 4px; background-color: #fef3c7; color: #92400e; font-weight: 500; font-size: 0.875rem;';
    }
}

// Initialize language and load capability detail
(async () => {
    await initLanguageSwitcher();
    loadCapability();
})();

