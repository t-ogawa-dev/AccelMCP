// capabilities/new.js - New Capability Registration Page
const pathParts = window.location.pathname.split('/');
const mcpServiceId = parseInt(pathParts[2]); // /mcp-services/{id}/apps/{app_id}/capabilities/new
const serviceId = parseInt(pathParts[4]);
let headerIndex = 0;
let bodyIndex = 0;

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

// Load accounts list
async function loadAccounts() {
    const response = await fetch('/api/accounts');
    const accounts = await response.json();
    
    const disabledSelect = document.getElementById('disabled-accounts');
    disabledSelect.innerHTML = accounts.map(account => 
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

// Fixed Parameters (key-value for query strings or fixed body params)
function addFixedParamRow(key = '', value = '') {
    const container = document.getElementById('fixed-params-container');
    const row = document.createElement('div');
    row.className = 'key-value-row';
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';
    row.innerHTML = `
        <input type="text" placeholder="Key" value="${key}" 
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <input type="text" placeholder="Value (or {{VARIABLE}})" value="${value}" 
               style="flex: 2; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
        <button type="button" onclick="this.parentElement.remove()" class="btn btn-sm btn-danger">${t('button_delete')}</button>
    `;
    container.appendChild(row);
}

// LLM Parameters (JSON Schema definition)
let llmParamIndex = 0;
function addLlmParamRow(paramData = null) {
    const container = document.getElementById('llm-params-container');
    const index = llmParamIndex++;
    
    const data = paramData || {
        name: '',
        type: 'string',
        description: '',
        required: false,
        enum: '',
        default: ''
    };
    
    const row = document.createElement('div');
    row.className = 'llm-param-row';
    row.setAttribute('data-index', index);
    row.style.cssText = 'border: 1px solid #cce5ff; border-radius: 4px; padding: 15px; margin-bottom: 15px; background: white;';
    row.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">パラメータ名 *</label>
                <input type="text" class="llm-param-name" value="${data.name}" placeholder="parameter_name"
                       style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;">
            </div>
            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">型 *</label>
                <select class="llm-param-type" onchange="toggleEnumField(this)" style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;">
                    <option value="string" ${data.type === 'string' ? 'selected' : ''}>string</option>
                    <option value="number" ${data.type === 'number' ? 'selected' : ''}>number</option>
                    <option value="integer" ${data.type === 'integer' ? 'selected' : ''}>integer</option>
                    <option value="boolean" ${data.type === 'boolean' ? 'selected' : ''}>boolean</option>
                    <option value="array" ${data.type === 'array' ? 'selected' : ''}>array</option>
                    <option value="object" ${data.type === 'object' ? 'selected' : ''}>object</option>
                    <option value="enum" ${data.type === 'enum' ? 'selected' : ''}>enum (選択肢)</option>
                </select>
            </div>
        </div>
        <div style="margin-bottom: 10px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">説明 (LLMに表示)</label>
            <input type="text" class="llm-param-description" value="${data.description}" placeholder="このパラメータの説明"
                   style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">デフォルト値</label>
                <input type="text" class="llm-param-default" value="${data.default}" placeholder="${data.type === 'enum' ? 'Enum値の1つを選択' : 'デフォルト値'}"
                       style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;">
                <small class="default-hint" style="display: ${data.type === 'enum' ? 'block' : 'none'}; color: #856404; font-size: 0.75rem; margin-top: 2px;">⚠️ Enum値の中から選んでください</small>
            </div>
            <div class="enum-field-container" style="display: ${data.type === 'enum' ? 'block' : 'none'};">
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">Enum値 (カンマ区切り) *</label>
                <input type="text" class="llm-param-enum" value="${data.enum}" placeholder="option1,option2,option3"
                       style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;">
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <label style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; cursor: pointer;">
                <input type="checkbox" class="llm-param-required" ${data.required ? 'checked' : ''}
                       style="width: 16px; height: 16px; cursor: pointer;">
                <span style="font-weight: 600; color: #333;">必須パラメータ</span>
            </label>
            <button type="button" onclick="this.closest('.llm-param-row').remove()" class="btn btn-sm btn-danger">削除</button>
        </div>
    `;
    container.appendChild(row);
}

// Toggle enum field visibility based on type selection
function toggleEnumField(selectElement) {
    const row = selectElement.closest('.llm-param-row');
    const enumContainer = row.querySelector('.enum-field-container');
    const defaultInput = row.querySelector('.llm-param-default');
    const defaultHint = row.querySelector('.default-hint');
    const selectedType = selectElement.value;
    
    if (selectedType === 'enum') {
        enumContainer.style.display = 'block';
        defaultInput.placeholder = 'Enum値の1つを選択';
        if (defaultHint) defaultHint.style.display = 'block';
    } else {
        enumContainer.style.display = 'none';
        defaultInput.placeholder = 'デフォルト値';
        if (defaultHint) defaultHint.style.display = 'none';
    }
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

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    
    // Initialize body type
    toggleBodyType();
    
    // Load accounts
    await loadAccounts();
    
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
        
        // Collect body parameters
        let bodyParams = {};
        if (method === 'GET') {
            // Collect fixed parameters
            const fixedParams = {};
            const fixedRows = document.querySelectorAll('#fixed-params-container .key-value-row');
            fixedRows.forEach(row => {
                const inputs = row.querySelectorAll('input[type="text"]');
                const key = inputs[0].value.trim();
                const value = inputs[1].value.trim();
                if (key) {
                    fixedParams[key] = value;
                }
            });
            
            // Collect LLM parameters and build JSON Schema
            const llmRows = document.querySelectorAll('#llm-params-container .llm-param-row');
            const properties = {};
            const required = [];
            
            llmRows.forEach(row => {
                const name = row.querySelector('.llm-param-name').value.trim();
                if (!name) return;
                
                const type = row.querySelector('.llm-param-type').value;
                const description = row.querySelector('.llm-param-description').value.trim();
                const defaultValue = row.querySelector('.llm-param-default').value.trim();
                const enumValue = row.querySelector('.llm-param-enum').value.trim();
                const isRequired = row.querySelector('.llm-param-required').checked;
                
                // For enum type, use string as the base type with enum constraint
                const propDef = { type: type === 'enum' ? 'string' : type };
                if (description) propDef.description = description;
                
                if (type === 'enum' && enumValue) {
                    propDef.enum = enumValue.split(',').map(v => v.trim()).filter(v => v);
                    
                    // Validate default value for enum
                    if (defaultValue && !propDef.enum.includes(defaultValue)) {
                        showError(`パラメータ "${name}": デフォルト値 "${defaultValue}" はEnum値 [${propDef.enum.join(', ')}] の中に存在しません。`);
                        row.querySelector('.llm-param-default').focus();
                        throw new Error('Invalid enum default value');
                    }
                }
                
                if (defaultValue) {
                    // Try to parse as JSON for proper type conversion
                    try {
                        propDef.default = JSON.parse(defaultValue);
                    } catch {
                        propDef.default = defaultValue;
                    }
                }
                
                properties[name] = propDef;
                if (isRequired) {
                    required.push(name);
                }
            });
            
            // Build final body_params structure
            if (Object.keys(properties).length > 0) {
                // MCP JSON Schema format with fixed params included
                bodyParams = {
                    type: 'object',
                    properties: properties,
                    required: required,
                    _fixed: fixedParams  // Store fixed params separately
                };
            } else if (Object.keys(fixedParams).length > 0) {
                // Only fixed params, no schema
                bodyParams = fixedParams;
            }
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
        
        // Add HTTP method to headers
        data.headers['X-HTTP-Method'] = method;
        
        // Collect enabled account IDs
        const enabledSelect = document.getElementById('enabled-accounts');
        const accountIds = Array.from(enabledSelect.options).map(opt => parseInt(opt.value));
        data.account_ids = accountIds;
        
        const response = await fetch(`/api/apps/${serviceId}/capabilities`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = `/mcp-services/${mcpServiceId}/apps/${serviceId}/capabilities`;
        } else {
            const error = await response.json();
            showError(t('capability_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
