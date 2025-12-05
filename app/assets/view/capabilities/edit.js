// capabilities/edit.js - Capability Edit Page
const capabilityId = parseInt(window.location.pathname.split('/')[2]);
let headerIndex = 0;
let bodyIndex = 0;
let currentAccessControl = 'public'; // デフォルトはpublic（制限なし）
let baseUrl = ''; // App's base URL

// Update URL preview
function updateUrlPreview() {
    const urlInput = document.getElementById('url');
    const urlPreviewBase = document.getElementById('url-preview-base');
    const urlPreviewPath = document.getElementById('url-preview-path');
    
    const inputPath = urlInput.value.trim();
    
    if (baseUrl) {
        // Show baseUrl + inputPath (or placeholder if empty)
        const separator = baseUrl.endsWith('/') || inputPath.startsWith('/') ? '' : '/';
        urlPreviewBase.textContent = baseUrl;
        
        if (inputPath && !inputPath.startsWith('http')) {
            urlPreviewPath.textContent = separator + inputPath;
        } else if (!inputPath) {
            urlPreviewPath.textContent = separator + '<input path>';
        } else {
            // Absolute URL entered
            urlPreviewPath.textContent = '';
        }
    } else {
        // No base URL - clear preview
        urlPreviewBase.textContent = '';
        urlPreviewPath.textContent = '';
    }
}

// Update access control UI
function updateAccessControlUI(isRestricted) {
    const permissionsSection = document.getElementById('permissions-section');
    
    if (isRestricted) {
        permissionsSection.style.display = 'block';
    } else {
        permissionsSection.style.display = 'none';
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('form-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Hide error message
function hideError() {
    const errorDiv = document.getElementById('form-error');
    errorDiv.style.display = 'none';
}

// Load account permissions
async function loadPermissions() {
    const response = await fetch(`/api/capabilities/${capabilityId}/permissions`);
    const data = await response.json();
    
    const enabledSelect = document.getElementById('enabled-accounts');
    const disabledSelect = document.getElementById('disabled-accounts');
    
    enabledSelect.innerHTML = data.enabled.map(account => 
        `<option value="${account.id}">${account.name}</option>`
    ).join('');
    
    disabledSelect.innerHTML = data.disabled.map(account => 
        `<option value="${account.id}">${account.name}</option>`
    ).join('');
    
    updateCounts();
}

function moveToEnabled() {
    const disabledSelect = document.getElementById('disabled-accounts');
    const enabledSelect = document.getElementById('enabled-accounts');
    const selected = Array.from(disabledSelect.selectedOptions);
    
    selected.forEach(option => {
        enabledSelect.appendChild(option);
    });
    
    updateCounts();
}

function moveAllToEnabled() {
    const disabledSelect = document.getElementById('disabled-accounts');
    const enabledSelect = document.getElementById('enabled-accounts');
    
    Array.from(disabledSelect.options).forEach(option => {
        enabledSelect.appendChild(option);
    });
    
    updateCounts();
}

function moveToDisabled() {
    const enabledSelect = document.getElementById('enabled-accounts');
    const disabledSelect = document.getElementById('disabled-accounts');
    const selected = Array.from(enabledSelect.selectedOptions);
    
    selected.forEach(option => {
        disabledSelect.appendChild(option);
    });
    
    updateCounts();
}

function moveAllToDisabled() {
    const enabledSelect = document.getElementById('enabled-accounts');
    const disabledSelect = document.getElementById('disabled-accounts');
    
    Array.from(enabledSelect.options).forEach(option => {
        disabledSelect.appendChild(option);
    });
    
    updateCounts();
}

function updateCounts() {
    const enabledCount = document.getElementById('enabled-accounts').options.length;
    const disabledCount = document.getElementById('disabled-accounts').options.length;
    
    document.getElementById('enabled-count').textContent = enabledCount;
    document.getElementById('disabled-count').textContent = disabledCount;
}

// Save permissions
async function savePermissions() {
    const enabledSelect = document.getElementById('enabled-accounts');
    const enabledAccountIds = Array.from(enabledSelect.options).map(opt => parseInt(opt.value));
    
    const response = await fetch(`/api/capabilities/${capabilityId}/permissions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_ids: enabledAccountIds })
    });
    
    if (!response.ok) {
        throw new Error('Failed to save permissions');
    }
}

function toggleBodyType() {
    const method = document.getElementById('method').value;
    const bodyKeyValue = document.getElementById('body-key-value');
    const bodyJson = document.getElementById('body-json');
    
    if (method === 'GET') {
        bodyKeyValue.style.display = 'block';
        bodyJson.style.display = 'none';
    } else {
        bodyKeyValue.style.display = 'none';
        bodyJson.style.display = 'block';
    }
}

function addHeaderRow(key = '', value = '', isReadOnly = false) {
    const container = document.getElementById('headers-container');
    const row = document.createElement('div');
    row.className = 'key-value-row';
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';
    
    const readOnlyStyle = isReadOnly ? 'background-color: #f5f5f5; cursor: not-allowed;' : '';
    const readOnlyAttr = isReadOnly ? 'readonly' : '';
    
    row.innerHTML = `
        <input type="text" placeholder="${t('form_key_placeholder')}" value="${key}" ${readOnlyAttr}
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; ${readOnlyStyle}">
        <input type="text" placeholder="${t('form_value_placeholder')}" value="${value}" ${readOnlyAttr}
               style="flex: 2; padding: 8px; border: 1px solid #ddd; border-radius: 4px; ${readOnlyStyle}">
        ${!isReadOnly ? `<button type="button" onclick="this.parentElement.remove()" class="btn btn-sm btn-danger">${t('button_delete')}</button>` : ''}
    `;
    container.appendChild(row);
    headerIndex++;
}

function addBodyRow(key = '', value = '', isReadOnly = false) {
    const container = document.getElementById('body-container');
    const row = document.createElement('div');
    row.className = 'key-value-row';
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';
    
    const readOnlyStyle = isReadOnly ? 'background-color: #f5f5f5; cursor: not-allowed;' : '';
    const readOnlyAttr = isReadOnly ? 'readonly' : '';
    
    row.innerHTML = `
        <input type="text" placeholder="${t('form_key_placeholder')}" value="${key}" ${readOnlyAttr}
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; ${readOnlyStyle}">
        <input type="text" placeholder="${t('form_value_placeholder')}" value="${value}" ${readOnlyAttr}
               style="flex: 2; padding: 8px; border: 1px solid #ddd; border-radius: 4px; ${readOnlyStyle}">
        ${!isReadOnly ? `<button type="button" onclick="this.parentElement.remove()" class="btn btn-sm btn-danger">${t('button_delete')}</button>` : ''}
    `;
    container.appendChild(row);
    bodyIndex++;
}

// JSON validation and formatting
function validateJson() {
    const textarea = document.getElementById('body_json');
    const errorDiv = document.getElementById('json-validation-error');
    const jsonText = textarea.value.trim();
    
    if (!jsonText) {
        errorDiv.style.display = 'none';
        return;
    }
    
    try {
        // Replace {{VARIABLE}} placeholders with dummy values for validation
        const testJson = jsonText.replace(/\{\{[^}]+\}\}/g, '"__VARIABLE__"');
        JSON.parse(testJson);
        errorDiv.style.display = 'block';
        errorDiv.style.color = '#28a745';
        errorDiv.innerHTML = '✓ ' + t('json_valid');
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 3000);
    } catch (e) {
        errorDiv.style.display = 'block';
        errorDiv.style.color = '#dc3545';
        errorDiv.innerHTML = '✗ ' + t('json_invalid') + ': ' + e.message;
    }
}

function formatJson() {
    const textarea = document.getElementById('body_json');
    const errorDiv = document.getElementById('json-validation-error');
    const jsonText = textarea.value.trim();
    
    if (!jsonText) {
        return;
    }
    
    try {
        // Extract variables before formatting
        const variables = [];
        const testJson = jsonText.replace(/\{\{([^}]+)\}\}/g, (match, varName) => {
            variables.push({ match, varName });
            return '"__VARIABLE_' + (variables.length - 1) + '__"';
        });
        
        const parsed = JSON.parse(testJson);
        let formatted = JSON.stringify(parsed, null, 2);
        
        // Restore variables in formatted JSON
        variables.forEach((v, index) => {
            formatted = formatted.replace('"__VARIABLE_' + index + '__"', v.match);
        });
        
        textarea.value = formatted;
        errorDiv.style.display = 'none';
    } catch (e) {
        errorDiv.style.display = 'block';
        errorDiv.style.color = '#dc3545';
        errorDiv.innerHTML = '✗ ' + t('json_invalid') + ': ' + e.message;
    }
}

async function loadCapability() {
    const response = await fetch(`/api/capabilities/${capabilityId}`);
    const cap = await response.json();
    
    // Get parent app information to check if it's MCP type and get base URL
    const appResponse = await fetch(`/api/apps/${cap.service_id}`);
    const app = await appResponse.json();
    const isMcpType = app.service_type === 'mcp';
    baseUrl = app.mcp_url || '';
    
    // Update breadcrumb links
    // Set breadcrumb links
    const mcpServiceId = cap.mcp_service_id || 1; // APIから取得するか、デフォルト値
    document.getElementById('mcp-service-link').href = `/mcp-services/${mcpServiceId}`;
    document.getElementById('apps-link').href = `/mcp-services/${mcpServiceId}/apps`;
    document.getElementById('service-link').href = `/mcp-services/${mcpServiceId}/apps/${cap.service_id}`;
    document.getElementById('capabilities-link').href = `/mcp-services/${mcpServiceId}/apps/${cap.service_id}/capabilities`;
    document.getElementById('detail-link').href = `/capabilities/${capabilityId}`;
    document.getElementById('cancel-link').href = `/capabilities/${capabilityId}`;
    
    document.getElementById('name').value = cap.name;
    document.getElementById('url').value = cap.url;
    document.getElementById('description').value = cap.description || '';
    
    // Add input event listener for URL preview
    const urlInput = document.getElementById('url');
    urlInput.addEventListener('input', updateUrlPreview);
    
    // Initial URL preview update
    updateUrlPreview();
    
    // Set access control (default: public for capabilities)
    currentAccessControl = cap.access_control || 'public';
    const isRestricted = currentAccessControl === 'restricted';
    document.getElementById('access-control-toggle').checked = isRestricted;
    updateAccessControlUI(isRestricted);
    
    // Get HTTP method from headers
    const method = cap.headers['X-HTTP-Method'] || 'POST';
    document.getElementById('method').value = method;
    
    // If MCP type, make fields read-only and hide URL/method fields
    if (isMcpType) {
        document.getElementById('name').readOnly = true;
        document.getElementById('url').readOnly = true;
        document.getElementById('description').readOnly = true;
        document.getElementById('method').disabled = true;
        
        // Hide URL and method fields for MCP type
        const urlFormGroup = document.getElementById('url').closest('.form-group');
        if (urlFormGroup) {
            urlFormGroup.style.display = 'none';
        }
        const methodFormGroup = document.getElementById('method').closest('.form-group');
        if (methodFormGroup) {
            methodFormGroup.style.display = 'none';
        }
        
        // Add visual indication
        ['name', 'description'].forEach(id => {
            const elem = document.getElementById(id);
            elem.style.backgroundColor = '#f5f5f5';
            elem.style.cursor = 'not-allowed';
        });
    }
    
    // Load headers (excluding X-HTTP-Method)
    const headers = { ...cap.headers };
    delete headers['X-HTTP-Method'];
    
    if (Object.keys(headers).length === 0) {
        if (!isMcpType) addHeaderRow(); // Add empty row if no headers (only for API type)
    } else {
        Object.entries(headers).forEach(([key, value]) => {
            addHeaderRow(key, value, isMcpType);
        });
    }
    
    // Hide "Add Header" button for MCP type
    if (isMcpType) {
        const addHeaderBtn = document.querySelector('button[onclick="addHeaderRow()"]');
        if (addHeaderBtn) addHeaderBtn.style.display = 'none';
    }
    
    // Load body parameters
    toggleBodyType();
    
    if (method === 'GET') {
        if (Object.keys(cap.body_params).length === 0) {
            if (!isMcpType) addBodyRow();
        } else {
            Object.entries(cap.body_params).forEach(([key, value]) => {
                addBodyRow(key, value, isMcpType);
            });
        }
    } else {
        const bodyJsonTextarea = document.getElementById('body_json');
        bodyJsonTextarea.value = JSON.stringify(cap.body_params, null, 2);
        
        if (isMcpType) {
            bodyJsonTextarea.readOnly = true;
            bodyJsonTextarea.style.backgroundColor = '#f5f5f5';
            bodyJsonTextarea.style.cursor = 'not-allowed';
            
            // Hide validation and format buttons
            const validateBtn = document.querySelector('button[onclick="validateJson()"]');
            const formatBtn = document.querySelector('button[onclick="formatJson()"]');
            if (validateBtn) validateBtn.style.display = 'none';
            if (formatBtn) formatBtn.style.display = 'none';
        }
    }
    
    // Hide "Add Body Parameter" button for MCP type
    if (isMcpType) {
        const addBodyBtn = document.querySelector('button[onclick="addBodyRow()"]');
        if (addBodyBtn) addBodyBtn.style.display = 'none';
    }
    
    return isMcpType;
}

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    const isMcpType = await loadCapability();
    await loadPermissions();
    
    // Setup access control toggle
    document.getElementById('access-control-toggle').addEventListener('change', async (e) => {
        const isRestricted = e.target.checked;
        updateAccessControlUI(isRestricted);
        currentAccessControl = isRestricted ? 'restricted' : 'public';
    });
    
    // Setup form submit handler
    document.getElementById('capability-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();
        
        const formData = new FormData(e.target);
        const method = formData.get('method');
        
        // Collect headers
        const headers = {};
        const headerRows = document.querySelectorAll('#headers-container .key-value-row');
        headerRows.forEach(row => {
            const inputs = row.querySelectorAll('input[type="text"]');
            const key = inputs[0].value.trim();
            const value = inputs[1].value.trim();
            if (key) {
                headers[key] = value;
            }
        });
        
        // Add HTTP method to headers
        headers['X-HTTP-Method'] = method;
        
        // Collect body parameters
        let bodyParams = {};
        if (method === 'GET') {
            const bodyRows = document.querySelectorAll('#body-container .key-value-row');
            bodyRows.forEach(row => {
                const inputs = row.querySelectorAll('input[type="text"]');
                const key = inputs[0].value.trim();
                const value = inputs[1].value.trim();
                if (key) {
                    bodyParams[key] = value;
                }
            });
        } else {
            const jsonText = document.getElementById('body_json').value.trim();
            if (jsonText) {
                try {
                    // Replace {{VARIABLE}} placeholders with dummy values for validation
                    const testJson = jsonText.replace(/\{\{[^}]+\}\}/g, '"__VARIABLE__"');
                    bodyParams = JSON.parse(testJson);
                    // Store original JSON with variables intact
                    bodyParams = jsonText;
                } catch (e) {
                    const errorDiv = document.getElementById('json-validation-error');
                    errorDiv.style.display = 'block';
                    errorDiv.style.color = '#dc3545';
                    errorDiv.innerHTML = '✗ ' + t('json_invalid') + ': ' + e.message;
                    document.getElementById('body_json').focus();
                    return;
                }
            }
        }
        
        // URL validation: skip if baseUrl exists (relative paths are valid)
        const urlValue = formData.get('url').trim();
        if (!baseUrl && urlValue) {
            // No baseUrl - must be absolute URL
            if (!urlValue.startsWith('http://') && !urlValue.startsWith('https://')) {
                showError(t('error_invalid_url') || 'URLを入力してください');
                document.getElementById('url').focus();
                return;
            }
        }
        
        const data = {
            name: formData.get('name'),
            capability_type: 'tool',
            url: urlValue,
            description: formData.get('description'),
            headers: headers,
            body_params: bodyParams
        };
        
        const response = await fetch(`/api/capabilities/${capabilityId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            showError(t('capability_update_failed') + ': ' + (error.error || t('error_unknown')));
            return;
        }
        
        // Update access control
        const accessControlResponse = await fetch(`/api/capabilities/${capabilityId}/access-control`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ access_control: currentAccessControl })
        });
        
        if (!accessControlResponse.ok) {
            showError('Failed to update access control');
            return;
        }
        
        // Save permissions if restricted
        if (currentAccessControl === 'restricted') {
            await savePermissions();
        }
        
        window.location.href = `/capabilities/${capabilityId}`;
    });
})();
