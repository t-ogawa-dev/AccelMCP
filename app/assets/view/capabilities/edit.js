// capabilities/edit.js - Capability Edit Page
const capabilityId = parseInt(window.location.pathname.split('/')[2]);
let headerIndex = 0;
let bodyIndex = 0;

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

function addHeaderRow(key = '', value = '') {
    const container = document.getElementById('headers-container');
    const row = document.createElement('div');
    row.className = 'key-value-row';
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';
    row.innerHTML = `
        <input type="text" placeholder="${t('form_key_placeholder')}" value="${key}" 
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <input type="text" placeholder="${t('form_value_placeholder')}" value="${value}" 
               style="flex: 2; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <button type="button" onclick="this.parentElement.remove()" class="btn btn-sm btn-danger">${t('button_delete')}</button>
    `;
    container.appendChild(row);
    headerIndex++;
}

function addBodyRow(key = '', value = '') {
    const container = document.getElementById('body-container');
    const row = document.createElement('div');
    row.className = 'key-value-row';
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';
    row.innerHTML = `
        <input type="text" placeholder="${t('form_key_placeholder')}" value="${key}" 
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <input type="text" placeholder="${t('form_value_placeholder')}" value="${value}" 
               style="flex: 2; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <button type="button" onclick="this.parentElement.remove()" class="btn btn-sm btn-danger">${t('button_delete')}</button>
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
        JSON.parse(jsonText);
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
        const parsed = JSON.parse(jsonText);
        textarea.value = JSON.stringify(parsed, null, 2);
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
    
    // Update breadcrumb links
    document.getElementById('service-link').href = `/services/${cap.service_id}`;
    document.getElementById('capabilities-link').href = `/services/${cap.service_id}/capabilities`;
    document.getElementById('detail-link').href = `/capabilities/${capabilityId}`;
    document.getElementById('cancel-link').href = `/capabilities/${capabilityId}`;
    
    document.getElementById('name').value = cap.name;
    document.getElementById('url').value = cap.url;
    document.getElementById('description').value = cap.description || '';
    
    // Get HTTP method from headers
    const method = cap.headers['X-HTTP-Method'] || 'POST';
    document.getElementById('method').value = method;
    
    // Load headers (excluding X-HTTP-Method)
    const headers = { ...cap.headers };
    delete headers['X-HTTP-Method'];
    
    if (Object.keys(headers).length === 0) {
        addHeaderRow(); // Add empty row if no headers
    } else {
        Object.entries(headers).forEach(([key, value]) => {
            addHeaderRow(key, value);
        });
    }
    
    // Load body parameters
    toggleBodyType();
    
    if (method === 'GET') {
        if (Object.keys(cap.body_params).length === 0) {
            addBodyRow();
        } else {
            Object.entries(cap.body_params).forEach(([key, value]) => {
                addBodyRow(key, value);
            });
        }
    } else {
        document.getElementById('body_json').value = JSON.stringify(cap.body_params, null, 2);
    }
}

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    await loadCapability();
    await loadPermissions();
    
    // Setup form submit handler
    document.getElementById('capability-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
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
                    bodyParams = JSON.parse(jsonText);
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
        
        const data = {
            name: formData.get('name'),
            capability_type: 'tool',
            url: formData.get('url'),
            description: formData.get('description'),
            headers: headers,
            body_params: bodyParams
        };
        
        // Collect enabled account IDs
        const enabledSelect = document.getElementById('enabled-accounts');
        const accountIds = Array.from(enabledSelect.options).map(opt => parseInt(opt.value));
        data.account_ids = accountIds;
        
        const response = await fetch(`/api/capabilities/${capabilityId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = `/capabilities/${capabilityId}`;
        } else {
            alert(t('capability_update_failed'));
        }
    });
})();
