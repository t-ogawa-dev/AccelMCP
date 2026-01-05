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

// Fixed Parameters (key-value for query strings or fixed body params)
function addFixedParamRow(key = '', value = '', isReadOnly = false) {
    const container = document.getElementById('fixed-params-container');
    const row = document.createElement('div');
    row.className = 'key-value-row';
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';
    
    const readOnlyStyle = isReadOnly ? 'background-color: #f5f5f5; cursor: not-allowed;' : '';
    const readOnlyAttr = isReadOnly ? 'readonly' : '';
    
    row.innerHTML = `
        <input type="text" placeholder="Key" value="${key}" ${readOnlyAttr}
               style="flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; ${readOnlyStyle}">
        <input type="text" placeholder="Value (or {{VARIABLE}})" value="${value}" ${readOnlyAttr}
               style="flex: 2; padding: 8px; border: 1px solid #ddd; border-radius: 4px; ${readOnlyStyle}">
        ${!isReadOnly ? `<button type="button" onclick="this.parentElement.remove()" class="btn btn-sm btn-danger">${t('button_delete')}</button>` : ''}
    `;
    container.appendChild(row);
}

// LLM Parameters (JSON Schema definition)
let llmParamIndex = 0;
function addLlmParamRow(paramData = null, isReadOnly = false) {
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
    
    const readOnlyStyle = isReadOnly ? 'background-color: #f5f5f5; cursor: not-allowed;' : '';
    const readOnlyAttr = isReadOnly ? 'readonly disabled' : '';
    
    const row = document.createElement('div');
    row.className = 'llm-param-row';
    row.setAttribute('data-index', index);
    row.style.cssText = 'border: 1px solid #cce5ff; border-radius: 4px; padding: 15px; margin-bottom: 15px; background: white;';
    row.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">パラメータ名 *</label>
                <input type="text" class="llm-param-name" value="${data.name}" placeholder="parameter_name" ${readOnlyAttr}
                       style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; ${readOnlyStyle}">
            </div>
            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">型 *</label>
                <select class="llm-param-type" ${readOnlyAttr} onchange="toggleEnumField(this)" style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; ${readOnlyStyle}">
                    <option value="string" ${data.type === 'string' ? 'selected' : ''}>string</option>
                    <option value="number" ${data.type === 'number' ? 'selected' : ''}>number</option>
                    <option value="integer" ${data.type === 'integer' ? 'selected' : ''}>integer</option>
                    <option value="boolean" ${data.type === 'boolean' ? 'selected' : ''}>boolean</option>
                    <option value="enum" ${data.type === 'enum' ? 'selected' : ''}>enum (選択肢)</option>
                </select>
                <small style="display: block; color: #6c757d; font-size: 0.75rem; margin-top: 2px;">※ GETメソッドではシンプルな型のみ使用可能</small>
            </div>
        </div>
        <div style="margin-bottom: 10px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">説明 (LLMに表示)</label>
            <input type="text" class="llm-param-description" value="${data.description}" placeholder="このパラメータの説明" ${readOnlyAttr}
                   style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; ${readOnlyStyle}">
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
            <div>
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">デフォルト値</label>
                <input type="text" class="llm-param-default" value="${data.default}" placeholder="${data.type === 'enum' ? 'Enum値の1つを選択' : 'デフォルト値'}" ${readOnlyAttr}
                       style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; ${readOnlyStyle}">
                <small class="default-hint" style="display: ${data.type === 'enum' ? 'block' : 'none'}; color: #856404; font-size: 0.75rem; margin-top: 2px;">⚠️ Enum値の中から選んでください</small>
            </div>
            <div class="enum-field-container" style="display: ${data.type === 'enum' ? 'block' : 'none'};">
                <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">Enum値 (カンマ区切り) *</label>
                <input type="text" class="llm-param-enum" value="${data.enum}" placeholder="option1,option2,option3" ${readOnlyAttr}
                       style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; ${readOnlyStyle}">
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <label style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; cursor: ${isReadOnly ? 'not-allowed' : 'pointer'};">
                <input type="checkbox" class="llm-param-required" ${data.required ? 'checked' : ''} ${readOnlyAttr}
                       style="width: 16px; height: 16px; cursor: ${isReadOnly ? 'not-allowed' : 'pointer'};">
                <span style="font-weight: 600; color: #333;">必須パラメータ</span>
            </label>
            ${!isReadOnly ? `<button type="button" onclick="this.closest('.llm-param-row').remove()" class="btn btn-sm btn-danger">削除</button>` : ''}
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

// Generate request sample based on current parameter definitions
function generateRequestSample() {
    const method = document.getElementById('method').value;
    const url = document.getElementById('url').value || '/api/endpoint';
    
    if (method === 'GET') {
        generateGetRequestSample(url);
    } else {
        generatePostRequestSample();
    }
}

function generateGetRequestSample(baseUrl) {
    const outputElement = document.getElementById('request-sample-output-get');
    
    // Collect fixed parameters
    const fixedParams = [];
    const fixedRows = document.querySelectorAll('#fixed-params-container .key-value-row');
    fixedRows.forEach(row => {
        const inputs = row.querySelectorAll('input[type="text"]');
        const key = inputs[0].value.trim();
        const value = inputs[1].value.trim();
        if (key) {
            // Query parameters don't need quotes - they're all strings by nature
            fixedParams.push(`${key}=${value}`);
        }
    });
    
    // Collect LLM parameters
    const llmParams = [];
    const llmRows = document.querySelectorAll('#llm-params-container .llm-param-row');
    llmRows.forEach(row => {
        const name = row.querySelector('.llm-param-name').value.trim();
        const type = row.querySelector('.llm-param-type').value;
        if (name) {
            let sampleValue;
            if (type === 'enum') {
                const enumValues = row.querySelector('.llm-param-enum').value.trim();
                sampleValue = enumValues ? enumValues.split(',')[0].trim() : '<string>';
            } else if (type === 'string') {
                sampleValue = '<string>';
            } else if (type === 'number' || type === 'integer') {
                sampleValue = '<number>';
            } else if (type === 'boolean') {
                sampleValue = '<boolean>';
            }
            llmParams.push(`${name}=${sampleValue}`);
        }
    });
    
    const allParams = [...fixedParams, ...llmParams];
    const queryString = allParams.length > 0 ? '?' + allParams.join('&') : '';
    const fullUrl = `${baseUrl}${queryString}`;
    
    outputElement.textContent = fullUrl || '(パラメータを追加してください)';
}

function generatePostRequestSample() {
    const outputElement = document.getElementById('request-sample-output-post');
    
    // Visual editor mode - build sample from tree
    const sampleBody = {};
    
    // Add fixed parameters from tree structure
    const fixedNodes = document.querySelectorAll('#fixed-params-post-container > .tree-node');
    fixedNodes.forEach(node => {
        const name = node.querySelector('.tree-param-name').value.trim();
        const type = node.querySelector('.tree-param-type').value;
        
        if (!name) return;
        
        // array型の場合、arrayValueフィールドから値を取得
        if (type === 'array') {
            const arrayItemsTypeSelect = node.querySelector('.tree-array-items-type');
            const itemsType = arrayItemsTypeSelect ? arrayItemsTypeSelect.value : 'string';
            
            if (itemsType === 'object') {
                // object配列の場合、オブジェクトのカンマ区切りを配列化
                const arrayObjectValueInput = node.querySelector('.tree-array-object-value');
                if (arrayObjectValueInput && arrayObjectValueInput.value.trim()) {
                    try {
                        const inputValue = arrayObjectValueInput.value.trim();
                        sampleBody[name] = JSON.parse(`[${inputValue}]`);
                    } catch (e) {
                        console.error('Invalid JSON for array object value:', e);
                        sampleBody[name] = [];
                    }
                }
            } else {
                // プリミティブ型配列の場合、CSV形式のinputから取得
                const arrayValueInput = node.querySelector('.tree-array-value');
                if (arrayValueInput && arrayValueInput.value.trim()) {
                    const csvValue = arrayValueInput.value.trim();
                    const arrayItems = csvValue.split(',').map(v => v.trim()).filter(v => v);
                    
                    // 型に応じて変換
                    if (itemsType === 'number') {
                        sampleBody[name] = arrayItems.map(v => parseFloat(v));
                    } else if (itemsType === 'integer') {
                        sampleBody[name] = arrayItems.map(v => parseInt(v));
                    } else if (itemsType === 'boolean') {
                        sampleBody[name] = arrayItems.map(v => v.toLowerCase() === 'true');
                    } else {
                        sampleBody[name] = arrayItems; // string
                    }
                }
            }
        } else if (type === 'object') {
            // object型の場合、子プロパティから値を構築
            const objValue = buildConstObjectValueFromChildren(node);
            
            // 子プロパティがない場合は、値フィールドからJSONをパース
            if (objValue) {
                sampleBody[name] = objValue;
            } else {
                const defaultValue = node.querySelector('.tree-param-default').value.trim();
                if (defaultValue) {
                    try {
                        sampleBody[name] = JSON.parse(defaultValue);
                    } catch (e) {
                        sampleBody[name] = defaultValue;
                    }
                }
            }
        } else {
            // 通常の型
            const defaultValue = node.querySelector('.tree-param-default').value.trim();
            if (defaultValue) {
                // Convert value based on type
                let value = defaultValue;
                if (type === 'number') {
                    value = parseFloat(defaultValue);
                } else if (type === 'integer') {
                    value = parseInt(defaultValue);
                } else if (type === 'boolean') {
                    value = defaultValue.toLowerCase() === 'true';
                }
                sampleBody[name] = value;
            }
        }
    });
    
    // Add LLM parameters from tree
    const rootNodes = document.querySelectorAll('#llm-params-tree-container > .tree-node');
    rootNodes.forEach(node => {
        const name = node.querySelector('.tree-param-name').value.trim();
        if (name) {
            sampleBody[name] = generateSampleValue(node);
        }
    });
    
    outputElement.textContent = JSON.stringify(sampleBody, null, 2);
}

function generateSampleValue(node) {
    const type = node.querySelector('.tree-param-type').value;
    
    if (type === 'string') {
        return '<string>';
    } else if (type === 'number' || type === 'integer') {
        return '<number>';
    } else if (type === 'boolean') {
        return '<boolean>';
    } else if (type === 'enum') {
        const enumValues = node.querySelector('.tree-param-enum').value.trim();
        return enumValues ? `"${enumValues.split(',')[0].trim()}"` : '<string>';
    } else if (type === 'array') {
        const itemsType = node.querySelector('.tree-array-items-type').value;
        if (itemsType === 'object') {
            // Build sample object from array item properties
            const arrayItemPropertiesContainer = node.querySelector('.tree-array-item-properties');
            const itemPropertyNodes = arrayItemPropertiesContainer.querySelectorAll(':scope > .tree-node');
            const sampleItem = {};
            itemPropertyNodes.forEach(itemNode => {
                const itemName = itemNode.querySelector('.tree-param-name').value.trim();
                if (itemName) {
                    sampleItem[itemName] = generateSampleValue(itemNode);
                }
            });
            return [sampleItem];
        } else {
            // Simple type array
            const sampleValue = itemsType === 'string' ? '<string>' : 
                               itemsType === 'number' || itemsType === 'integer' ? '<number>' : 
                               itemsType === 'boolean' ? '<boolean>' : '<value>';
            return [sampleValue];
        }
    } else if (type === 'object') {
        const childrenContainer = node.querySelector('.tree-children');
        const childNodes = childrenContainer.querySelectorAll(':scope > .tree-node');
        const sampleObj = {};
        childNodes.forEach(childNode => {
            const childName = childNode.querySelector('.tree-param-name').value.trim();
            if (childName) {
                sampleObj[childName] = generateSampleValue(childNode);
            }
        });
        return sampleObj;
    }
    
    return '<value>';
}

// ============================================
// POST Method: Hierarchical Tree Editor
// ============================================

// Fixed Parameters for POST
let fixedParamPostIndex = 0;
// 固定パラメータ(POST用・階層対応)
function addFixedParamPostRow(containerOrParent = null, depth = 0, paramData = null, isReadOnly = false) {
    // 階層エディタを使用
    return addLlmParamTreeRow(containerOrParent || document.getElementById('fixed-params-post-container'), depth, paramData, isReadOnly);
}

// Tree-based hierarchical editor for LLM Parameters (POST)
let treeNodeIdCounter = 0;

function addLlmParamTreeRow(containerOrParent = null, depth = 0, paramData = null) {
    const nodeId = treeNodeIdCounter++;
    
    // containerOrParentが配列コンテナ要素かどうかをチェック
    let container;
    if (!containerOrParent) {
        // ルート要素の場合
        container = document.getElementById('llm-params-tree-container');
    } else if (containerOrParent.classList && (containerOrParent.classList.contains('tree-children') || containerOrParent.classList.contains('tree-array-item-properties'))) {
        // 既にコンテナ要素が渡されている場合
        container = containerOrParent;
    } else if (containerOrParent.id === 'llm-params-tree-container' || containerOrParent.id === 'fixed-params-post-container') {
        // ルートコンテナが直接渡されている場合
        container = containerOrParent;
    } else if (containerOrParent.classList && containerOrParent.classList.contains('tree-node')) {
        // 親ノードが渡されている場合（後方互換性）
        container = containerOrParent.querySelector('.tree-children');
    } else {
        // その他の場合（旧コードとの互換性）
        container = containerOrParent;
    }
    
    if (!container) {
        console.error('Container not found for:', containerOrParent);
        return null;
    }
    
    // Check if this is for fixed parameters (not LLM parameters)
    const isFixedParam = container.id === 'fixed-params-post-container' || 
                         container.closest('#fixed-params-post-container') !== null;
    
    const data = paramData || {
        name: '',
        type: 'string',
        description: '',
        required: false,
        enum: '',
        default: '',
        children: [],
        itemsType: 'string'
    };
    
    const node = document.createElement('div');
    node.className = 'tree-node';
    node.setAttribute('data-node-id', nodeId);
    node.setAttribute('data-depth', depth);
    node.style.cssText = `margin-left: ${depth * 20}px; border: 1px solid #cce5ff; border-radius: 4px; padding: 10px; margin-bottom: 10px; background: white;`;
    
    const isExpandable = data.type === 'object';
    const hasChildren = data.children && data.children.length > 0;
    const expandIcon = isExpandable ? (hasChildren ? '▼' : '▶') : '';
    
    node.innerHTML = `
        <div class="tree-node-header" style="display: flex; gap: 10px; align-items: center; margin-bottom: 8px;">
            <button type="button" class="expand-btn" onclick="toggleTreeNode(${nodeId})" 
                    style="width: 24px; height: 24px; border: none; background: #f0f0f0; border-radius: 4px; cursor: pointer; font-size: 0.8rem; display: ${isExpandable ? 'block' : 'none'};">
                ${expandIcon}
            </button>
            <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr 2fr auto; gap: 8px; align-items: center;">
                <div style="display: flex; align-items: center;">
                    <input type="text" class="tree-param-name" placeholder="param_name"
                           style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                </div>
                <div style="display: flex; align-items: center;">
                    <select class="tree-param-type" onchange="handleTreeTypeChange(${nodeId})" 
                            style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                        <option value="string" ${data.type === 'string' ? 'selected' : ''}>string</option>
                        <option value="number" ${data.type === 'number' ? 'selected' : ''}>number</option>
                        <option value="integer" ${data.type === 'integer' ? 'selected' : ''}>integer</option>
                        <option value="boolean" ${data.type === 'boolean' ? 'selected' : ''}>boolean</option>
                        ${!isFixedParam ? `<option value="enum" ${data.type === 'enum' ? 'selected' : ''}>enum</option>` : ''}
                        <option value="object" ${data.type === 'object' ? 'selected' : ''}>object</option>
                        <option value="array" ${data.type === 'array' ? 'selected' : ''}>array</option>
                    </select>
                </div>
                <div style="display: ${isFixedParam ? 'none' : 'flex'}; align-items: center;">
                    <input type="text" class="tree-param-description" placeholder="説明"
                           style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                </div>
                <div style="display: flex; gap: 8px; align-items: center; justify-content: center;">
                    <label style="display: ${isFixedParam ? 'none' : 'flex'}; align-items: center; gap: 4px; cursor: pointer; font-size: 0.85rem; white-space: nowrap; margin-bottom: 0;">
                        <input type="checkbox" class="tree-param-required" ${data.required ? 'checked' : ''}
                               style="width: 16px; height: 16px; margin: 0;">
                        <span style="color: #333;">必須</span>
                    </label>
                    <button type="button" onclick="removeTreeNode(${nodeId})" class="btn btn-sm btn-danger" style="padding: 4px 8px; font-size: 0.8rem;">×</button>
                </div>
            </div>
        </div>
        
        <!-- Enum values field (shown when type is enum) -->
        <div class="tree-enum-field" style="display: ${data.type === 'enum' ? 'block' : 'none'}; margin-bottom: 8px; margin-left: 34px;">
            <input type="text" class="tree-param-enum" placeholder="option1,option2,option3"
                   style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
            <small style="display: block; color: #6c757d; font-size: 0.75rem; margin-top: 2px;">カンマ区切りで選択肢を入力</small>
        </div>
        
        <!-- Default value field -->
        <div class="tree-default-field tree-default-value-field" style="display: ${data.type === 'object' || data.type === 'array' ? 'none' : 'block'}; margin-bottom: 8px; margin-left: 34px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;" class="tree-default-label">${isFixedParam ? '値:' : 'デフォルト値:'}</label>
            ${
                data.type === 'boolean' ?
                (isFixedParam ?
                    `<select class="tree-param-default" style="width: 200px; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                        <option value="true" ${data.default === true || data.default === 'true' || !data.default ? 'selected' : ''}>true</option>
                        <option value="false" ${data.default === false || data.default === 'false' ? 'selected' : ''}>false</option>
                    </select>` :
                    `<select class="tree-param-default" style="width: 200px; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                        <option value="" ${!data.default && data.default !== false ? 'selected' : ''}>未設定</option>
                        <option value="true" ${data.default === true || data.default === 'true' ? 'selected' : ''}>true</option>
                        <option value="false" ${data.default === false || data.default === 'false' ? 'selected' : ''}>false</option>
                    </select>`
                ) :
                `<input type="text" class="tree-param-default" placeholder="${isFixedParam ? '値' : 'デフォルト値'}" style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">`
            }
        </div>
        
        <!-- Array items type field (shown when type is array) -->
        <div class="tree-array-items-field" style="display: ${data.type === 'array' ? 'block' : 'none'}; margin-bottom: 8px; margin-left: 34px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">配列要素の型:</label>
            <select class="tree-array-items-type" style="width: 200px; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                <option value="string" ${data.itemsType === 'string' ? 'selected' : ''}>string</option>
                <option value="number" ${data.itemsType === 'number' ? 'selected' : ''}>number</option>
                <option value="integer" ${data.itemsType === 'integer' ? 'selected' : ''}>integer</option>
                <option value="boolean" ${data.itemsType === 'boolean' ? 'selected' : ''}>boolean</option>
                <option value="object" ${data.itemsType === 'object' ? 'selected' : ''}>object</option>
            </select>
        </div>
        
        <!-- Array value field (shown for fixed params with array type and non-object items) -->
        <div class="tree-array-value-field" style="display: ${isFixedParam && data.type === 'array' && data.itemsType !== 'object' ? 'block' : 'none'}; margin-bottom: 8px; margin-left: 34px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">値 (カンマ区切り):</label>
            <input type="text" class="tree-array-value" placeholder="${
                data.itemsType === 'string' ? 'value1, value2, value3' :
                data.itemsType === 'number' || data.itemsType === 'integer' ? '1, 2, 3' :
                data.itemsType === 'boolean' ? 'true, false, true' : ''
            }" style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
        </div>
        
        <!-- Array object value field (shown for fixed params with array type and object items) -->
        <div class="tree-array-object-value-field" style="display: ${isFixedParam && data.type === 'array' && data.itemsType === 'object' ? 'block' : 'none'}; margin-bottom: 8px; margin-left: 34px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">値 (オブジェクトをカンマ区切り):</label>
            <textarea class="tree-array-object-value" rows="4" placeholder='{"key": "value"}, {"key": "value"}' style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; font-family: monospace;"></textarea>
        </div>
        
        <!-- Object value field (shown for fixed params with object type at depth >= 1) -->
        <div class="tree-object-value-field" style="display: ${isFixedParam && data.type === 'object' && depth >= 1 ? 'block' : 'none'}; margin-bottom: 8px; margin-left: 34px;">
            <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;">値 (JSON形式):</label>
            <textarea class="tree-param-default" rows="4" placeholder='{"key": "value"}' style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; font-family: monospace;"></textarea>
        </div>
        
        <!-- Children container (for object type) -->
        <div class="tree-children" style="display: ${isExpandable && hasChildren ? 'block' : 'none'}; margin-left: 20px; margin-top: 10px;"></div>
        
        <!-- Add child button (for object type) -->
        <div class="tree-add-child" style="display: ${data.type === 'object' && (!isFixedParam || depth === 0) ? 'block' : 'none'}; margin-left: 34px; margin-top: 8px;">
            <button type="button" onclick="addChildToTreeNode(${nodeId})" class="btn btn-sm btn-secondary" style="padding: 4px 10px; font-size: 0.8rem;">+ 子プロパティを追加</button>
        </div>
        
        <!-- Add array item property button (for array type with object items) -->
        <div class="tree-add-array-item-property" style="display: ${data.type === 'array' && data.itemsType === 'object' ? 'block' : 'none'}; margin-left: 34px; margin-top: 8px;">
            <button type="button" onclick="addArrayItemPropertyNode(${nodeId})" class="btn btn-sm btn-secondary" style="padding: 4px 10px; font-size: 0.8rem;">+ 配列要素のプロパティを定義</button>
        </div>
        
        <!-- Children container (for object type) -->
        <div class="tree-children" style="display: ${isExpandable && hasChildren ? 'block' : 'none'}; margin-left: 20px; margin-top: 10px;"></div>
        
        <!-- Array item properties container (for array type with object items) -->
        <div class="tree-array-item-properties" style="margin-left: 20px; margin-top: 10px;"></div>
    `;
    
    container.appendChild(node);
    
    // Set input values after DOM insertion to avoid template literal issues
    const nameInput = node.querySelector('.tree-param-name');
    const descInput = node.querySelector('.tree-param-description');
    const enumInput = node.querySelector('.tree-param-enum');
    const defaultInput = node.querySelector('.tree-param-default');
    
    if (nameInput) nameInput.value = data.name || '';
    if (descInput) descInput.value = data.description || '';
    if (enumInput) enumInput.value = data.enum || '';
    // boolean型selectboxの場合はtemplate内のselected属性で値が設定されているためスキップ
    if (defaultInput && defaultInput.tagName !== 'SELECT') {
        defaultInput.value = data.default || '';
    }
    
    // Set array value for fixed params with array type
    const arrayValueInput = node.querySelector('.tree-array-value');
    if (arrayValueInput) {
        arrayValueInput.value = data.arrayValue || '';
    }
    
    // Set array object value for fixed params with array+object type
    const arrayObjectValueInput = node.querySelector('.tree-array-object-value');
    if (arrayObjectValueInput) {
        arrayObjectValueInput.value = data.arrayObjectValue || '';
    }
    
    // Set object value for fixed params with object type at depth >= 1
    if (isFixedParam && data.type === 'object' && depth >= 1) {
        const objectValueInput = node.querySelector('.tree-object-value-field .tree-param-default');
        if (objectValueInput && data.default) {
            objectValueInput.value = typeof data.default === 'object' ? JSON.stringify(data.default, null, 2) : data.default;
        }
    }
    
    // Recursively add children if any
    if (data.children && data.children.length > 0) {
        data.children.forEach(child => {
            addLlmParamTreeRow(node, depth + 1, child);
        });
    }
    
    // Recursively add array items properties if any
    if (data.itemsProperties && data.itemsProperties.length > 0) {
        const arrayItemPropertiesContainer = node.querySelector('.tree-array-item-properties');
        data.itemsProperties.forEach(itemProp => {
            addLlmParamTreeRow(arrayItemPropertiesContainer, depth + 1, itemProp);
        });
    }
    
    return node;
}

function toggleTreeNode(nodeId) {
    const node = document.querySelector(`.tree-node[data-node-id="${nodeId}"]`);
    if (!node) return;
    
    const expandBtn = node.querySelector('.expand-btn');
    const childrenContainer = node.querySelector('.tree-children');
    
    if (childrenContainer.style.display === 'none') {
        childrenContainer.style.display = 'block';
        expandBtn.textContent = '▼';
    } else {
        childrenContainer.style.display = 'none';
        expandBtn.textContent = '▶';
    }
}

function handleTreeTypeChange(nodeId) {
    const node = document.querySelector(`.tree-node[data-node-id="${nodeId}"]`);
    if (!node) return;
    
    const typeSelect = node.querySelector('.tree-param-type');
    const selectedType = typeSelect.value;
    
    const enumField = node.querySelector('.tree-enum-field');
    const arrayItemsField = node.querySelector('.tree-array-items-field');
    const addChildBtn = node.querySelector('.tree-add-child');
    const addArrayItemPropertyBtn = node.querySelector('.tree-add-array-item-property');
    const expandBtn = node.querySelector('.expand-btn');
    const childrenContainer = node.querySelector('.tree-children');
    const defaultFieldContainer = node.querySelector('.tree-default-value-field');
    
    // 固定パラメータとdepthチェック
    const isFixedParam = node.closest('#fixed-params-post-container') !== null;
    const depth = parseInt(node.getAttribute('data-depth')) || 0;
    
    // Show/hide fields based on type
    enumField.style.display = selectedType === 'enum' ? 'block' : 'none';
    arrayItemsField.style.display = selectedType === 'array' ? 'block' : 'none';
    // 固定パラメータの場合、depth=0のみ子追加可能
    addChildBtn.style.display = (selectedType === 'object' && (!isFixedParam || depth === 0)) ? 'block' : 'none';
    expandBtn.style.display = selectedType === 'object' ? 'block' : 'none';
    
    // デフォルト値/値フィールド表示制御とフィールド再構築
    if (defaultFieldContainer) {
        const shouldShow = selectedType !== 'object' && selectedType !== 'array';
        defaultFieldContainer.style.display = shouldShow ? 'block' : 'none';
        
        if (shouldShow) {
            // 現在の値を保持
            const currentInput = defaultFieldContainer.querySelector('.tree-param-default');
            const currentValue = currentInput ? currentInput.value : '';
            
            // ラベルテキストを判定（固定パラメータか否か）
            const label = defaultFieldContainer.querySelector('.tree-default-label');
            const isFixedParam = label && label.textContent.includes('値:');
            const labelText = isFixedParam ? '値:' : 'デフォルト値:';
            const placeholderText = isFixedParam ? '値' : 'デフォルト値';
            
            // フィールドを再構築
            if (selectedType === 'boolean') {
                if (isFixedParam) {
                    // 固定パラメータ: true/falseのみ、デフォルトtrue
                    defaultFieldContainer.innerHTML = `
                        <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;" class="tree-default-label">${labelText}</label>
                        <select class="tree-param-default" style="width: 200px; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                            <option value="true" ${currentValue === 'true' || !currentValue ? 'selected' : ''}>true</option>
                            <option value="false" ${currentValue === 'false' ? 'selected' : ''}>false</option>
                        </select>
                    `;
                } else {
                    // LLMパラメータ: 未設定/true/false
                    defaultFieldContainer.innerHTML = `
                        <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;" class="tree-default-label">${labelText}</label>
                        <select class="tree-param-default" style="width: 200px; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                            <option value="" ${!currentValue ? 'selected' : ''}>未設定</option>
                            <option value="true" ${currentValue === 'true' ? 'selected' : ''}>true</option>
                            <option value="false" ${currentValue === 'false' ? 'selected' : ''}>false</option>
                        </select>
                    `;
                }
            } else {
                // booleanから変更された場合はtrue/false値をクリア
                const shouldClearValue = (currentValue === 'true' || currentValue === 'false');
                defaultFieldContainer.innerHTML = `
                    <label style="font-size: 0.85rem; font-weight: 600; color: #333; display: block; margin-bottom: 4px;" class="tree-default-label">${labelText}</label>
                    <input type="text" class="tree-param-default" placeholder="${placeholderText}" value="${shouldClearValue ? '' : currentValue}" style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                `;
            }
        }
    }
    
    // Array items object control
    const arrayValueField = node.querySelector('.tree-array-value-field');
    const arrayObjectValueField = node.querySelector('.tree-array-object-value-field');
    const objectValueField = node.querySelector('.tree-object-value-field');
    
    if (selectedType === 'array') {
        const itemsType = node.querySelector('.tree-array-items-type').value;
        const isFixedParam = node.closest('#fixed-params-post-container') !== null;
        
        // 固定パラメータの場合はボタンを非表示（JSON直接入力するため）
        addArrayItemPropertyBtn.style.display = (itemsType === 'object' && !isFixedParam) ? 'block' : 'none';
        
        // array値フィールド：固定パラメータの場合のみ表示
        if (arrayValueField) {
            arrayValueField.style.display = (isFixedParam && itemsType !== 'object') ? 'block' : 'none';
        }
        if (arrayObjectValueField) {
            arrayObjectValueField.style.display = (isFixedParam && itemsType === 'object') ? 'block' : 'none';
        }
        if (objectValueField) {
            objectValueField.style.display = 'none';
        }
    } else if (selectedType === 'object') {
        addArrayItemPropertyBtn.style.display = 'none';
        if (arrayValueField) arrayValueField.style.display = 'none';
        if (arrayObjectValueField) arrayObjectValueField.style.display = 'none';
        // 固定パラメータのdepth>=1の場合、object値フィールドを表示
        if (objectValueField) {
            objectValueField.style.display = (isFixedParam && depth >= 1) ? 'block' : 'none';
        }
    } else {
        addArrayItemPropertyBtn.style.display = 'none';
        if (arrayValueField) arrayValueField.style.display = 'none';
        if (arrayObjectValueField) arrayObjectValueField.style.display = 'none';
        if (objectValueField) objectValueField.style.display = 'none';
    }
    
    // If changing away from object, hide children
    if (selectedType !== 'object') {
        childrenContainer.style.display = 'none';
    }
}

function handleArrayItemsTypeChange(nodeId) {
    const node = document.querySelector(`.tree-node[data-node-id="${nodeId}"]`);
    if (!node) return;
    
    const itemsType = node.querySelector('.tree-array-items-type').value;
    const addArrayItemPropertyBtn = node.querySelector('.tree-add-array-item-property');
    const arrayValueField = node.querySelector('.tree-array-value-field');
    const arrayObjectValueField = node.querySelector('.tree-array-object-value-field');
    
    const isFixedParam = node.closest('#fixed-params-post-container') !== null;
    
    // 固定パラメータの場合はボタンを非表示（JSON直接入力するため）
    addArrayItemPropertyBtn.style.display = (itemsType === 'object' && !isFixedParam) ? 'block' : 'none';
    
    // array値フィールド：固定パラメータの場合のみ表示
    if (arrayValueField) {
        arrayValueField.style.display = (isFixedParam && itemsType !== 'object') ? 'block' : 'none';
        
        // プリミティブ型の場合、プレースホルダーを更新
        if (itemsType !== 'object') {
            const arrayValueInput = arrayValueField.querySelector('.tree-array-value');
            if (arrayValueInput) {
                if (itemsType === 'string') {
                    arrayValueInput.placeholder = 'value1, value2, value3';
                } else if (itemsType === 'number' || itemsType === 'integer') {
                    arrayValueInput.placeholder = '1, 2, 3';
                } else if (itemsType === 'boolean') {
                    arrayValueInput.placeholder = 'true, false, true';
                }
            }
        }
    }
    
    // array object値フィールド：object型の場合のみ表示
    if (arrayObjectValueField) {
        arrayObjectValueField.style.display = (isFixedParam && itemsType === 'object') ? 'block' : 'none';
    }
}

function addChildToTreeNode(parentNodeId) {
    const parentNode = document.querySelector(`.tree-node[data-node-id="${parentNodeId}"]`);
    if (!parentNode) return;
    
    const depth = parseInt(parentNode.getAttribute('data-depth')) + 1;
    const childrenContainer = parentNode.querySelector('.tree-children');
    
    if (childrenContainer) {
        addLlmParamTreeRow(childrenContainer, depth);
        
        // Show children container and update expand button
        childrenContainer.style.display = 'block';
        const expandBtn = parentNode.querySelector('.expand-btn');
        if (expandBtn) expandBtn.textContent = '▼';
    }
}

function addArrayItemPropertyNode(nodeId) {
    const parentNode = document.querySelector(`.tree-node[data-node-id="${nodeId}"]`);
    if (!parentNode) return;
    
    const arrayItemPropertiesContainer = parentNode.querySelector('.tree-array-item-properties');
    const depth = parseInt(parentNode.dataset.depth) + 1;
    
    if (arrayItemPropertiesContainer) {
        addLlmParamTreeRow(arrayItemPropertiesContainer, depth);
        arrayItemPropertiesContainer.style.display = 'block';
    }
}

function removeTreeNode(nodeId) {
    const node = document.querySelector(`.tree-node[data-node-id="${nodeId}"]`);
    if (node) {
        node.remove();
    }
}

// 固定パラメータのobject型子プロパティから値オブジェクトを構築
function buildConstObjectValueFromChildren(node) {
    const childrenContainer = node.querySelector('.tree-children');
    if (!childrenContainer) return null;
    
    const childNodes = childrenContainer.querySelectorAll(':scope > .tree-node');
    if (childNodes.length === 0) return null;
    
    const obj = {};
    childNodes.forEach(childNode => {
        const nameInput = childNode.querySelector('.tree-param-name');
        const typeSelect = childNode.querySelector('.tree-param-type');
        
        if (!nameInput || !typeSelect) return;
        
        const name = nameInput.value.trim();
        if (!name) return;
        
        const type = typeSelect.value;
        
        // 型に応じて値を取得
        if (type === 'array') {
            // array型: 配列要素の型を確認
            const arrayItemsTypeSelect = childNode.querySelector('.tree-array-items-type');
            const itemsType = arrayItemsTypeSelect ? arrayItemsTypeSelect.value : 'string';
            
            if (itemsType === 'object') {
                // object配列: tree-array-object-valueからJSON取得
                const arrayObjectValueInput = childNode.querySelector('.tree-array-object-value');
                if (arrayObjectValueInput && arrayObjectValueInput.value.trim()) {
                    try {
                        const inputValue = arrayObjectValueInput.value.trim();
                        obj[name] = JSON.parse(`[${inputValue}]`);
                    } catch (e) {
                        console.error('Invalid JSON for array object value:', e);
                        obj[name] = [];
                    }
                } else {
                    obj[name] = [];
                }
            } else {
                // プリミティブ型配列: tree-array-valueからCSV取得
                const arrayValueInput = childNode.querySelector('.tree-array-value');
                if (arrayValueInput && arrayValueInput.value.trim()) {
                    const csvValue = arrayValueInput.value.trim();
                    const arrayItems = csvValue.split(',').map(v => v.trim()).filter(v => v);
                    
                    // 型に応じて変換
                    if (itemsType === 'number') {
                        obj[name] = arrayItems.map(v => parseFloat(v));
                    } else if (itemsType === 'integer') {
                        obj[name] = arrayItems.map(v => parseInt(v));
                    } else if (itemsType === 'boolean') {
                        obj[name] = arrayItems.map(v => v.toLowerCase() === 'true');
                    } else {
                        obj[name] = arrayItems; // string
                    }
                } else {
                    obj[name] = [];
                }
            }
        } else if (type === 'object') {
            // 2階層目のobject: まず子プロパティから再帰的に構築を試み、なければtextareaからJSON取得
            const nestedObj = buildConstObjectValueFromChildren(childNode);
            if (nestedObj) {
                obj[name] = nestedObj;
            } else {
                // tree-object-value-field内のtextareaから取得
                const objectValueField = childNode.querySelector('.tree-object-value-field');
                if (objectValueField) {
                    const textarea = objectValueField.querySelector('.tree-param-default');
                    const value = textarea ? textarea.value.trim() : '';
                    if (value) {
                        try {
                            obj[name] = JSON.parse(value);
                        } catch (e) {
                            console.error('Invalid JSON for nested object:', e);
                        }
                    }
                }
            }
        } else {
            // その他の型: tree-default-value-field内のinputから取得
            const defaultValueField = childNode.querySelector('.tree-default-value-field');
            if (!defaultValueField) return;
            
            const defaultInput = defaultValueField.querySelector('.tree-param-default');
            if (!defaultInput) return;
            
            const value = defaultInput.value.trim();
            if (!value) return;
            
            // 型に応じて値を変換
            if (type === 'number') {
                obj[name] = parseFloat(value);
            } else if (type === 'integer') {
                obj[name] = parseInt(value);
            } else if (type === 'boolean') {
                obj[name] = value.toLowerCase() === 'true';
            } else {
                obj[name] = value;
            }
        }
    });
    
    return Object.keys(obj).length > 0 ? obj : null;
}

// Build JSON Schema from tree structure
function buildSchemaFromTree() {
    const properties = {};
    const required = [];
    
    // 固定パラメータをconst制約付きでpropertiesに含める
    const fixedContainer = document.getElementById('fixed-params-post-container');
    const fixedNodes = Array.from(fixedContainer.children).filter(child => child.classList.contains('tree-node'));
    
    fixedNodes.forEach(node => {
        const name = node.querySelector('.tree-param-name').value.trim();
        if (!name) return;
        
        const propDef = buildPropertyFromNode(node);
        const typeSelect = node.querySelector('.tree-param-type');
        const type = typeSelect.value;
        
        let constValue;
        
        // array型の場合、arrayValueフィールドからCSV値を取得して配列に変換
        if (type === 'array') {
            const arrayItemsTypeSelect = node.querySelector('.tree-array-items-type');
            const itemsType = arrayItemsTypeSelect ? arrayItemsTypeSelect.value : 'string';
            
            if (itemsType === 'object') {
                // object配列の場合、オブジェクトのカンマ区切りを配列化
                const arrayObjectValueInput = node.querySelector('.tree-array-object-value');
                if (arrayObjectValueInput && arrayObjectValueInput.value.trim()) {
                    try {
                        // 入力値を[]で囲んで配列としてパース
                        const inputValue = arrayObjectValueInput.value.trim();
                        constValue = JSON.parse(`[${inputValue}]`);
                        // 配列であることを確認
                        if (!Array.isArray(constValue)) {
                            console.error('Array object value must be an array');
                            constValue = [];
                        }
                    } catch (e) {
                        console.error('Invalid JSON for array object value:', e);
                        constValue = [];
                    }
                } else {
                    constValue = [];
                }
            } else {
                // プリミティブ型配列の場合、CSV形式のinputから取得
                const arrayValueInput = node.querySelector('.tree-array-value');
                if (arrayValueInput && arrayValueInput.value.trim()) {
                    const csvValue = arrayValueInput.value.trim();
                    const arrayItems = csvValue.split(',').map(v => v.trim()).filter(v => v);
                    
                    // 型に応じて配列要素を変換
                    if (itemsType === 'number') {
                        constValue = arrayItems.map(v => parseFloat(v));
                    } else if (itemsType === 'integer') {
                        constValue = arrayItems.map(v => parseInt(v));
                    } else if (itemsType === 'boolean') {
                        constValue = arrayItems.map(v => v.toLowerCase() === 'true');
                    } else {
                        constValue = arrayItems; // string
                    }
                } else {
                    constValue = []; // 空配列
                }
            }
        } else if (type === 'object') {
            // object型の場合、子プロパティから値を構築
            constValue = buildConstObjectValueFromChildren(node);
            
            // 子プロパティがない場合は、値フィールドからJSONをパース
            if (!constValue) {
                const defaultValue = node.querySelector('.tree-param-default').value.trim();
                if (defaultValue) {
                    try {
                        constValue = JSON.parse(defaultValue);
                    } catch (e) {
                        constValue = defaultValue;
                    }
                }
            }
        } else {
            // 通常の値フィールドから取得
            const defaultValue = node.querySelector('.tree-param-default').value.trim();
            
            if (defaultValue) {
                // 型に応じて値を変換
                if (propDef.type === 'number' || propDef.type === 'integer') {
                    constValue = propDef.type === 'integer' ? parseInt(defaultValue) : parseFloat(defaultValue);
                } else if (propDef.type === 'boolean') {
                    constValue = defaultValue.toLowerCase() === 'true';
                } else {
                    constValue = defaultValue;
                }
            }
        }
        
        if (constValue !== undefined && constValue !== null && constValue !== '') {
            properties[name] = {
                ...propDef,
                const: constValue,
                default: constValue,
                description: propDef.description || '固定値パラメータ（変更不可）'
            };
            // 固定パラメータは常にrequiredに含める
            required.push(name);
        }
    });
    
    // LLMパラメータを追加
    const treeContainer = document.getElementById('llm-params-tree-container');
    const rootNodes = Array.from(treeContainer.children).filter(child => child.classList.contains('tree-node'));
    
    rootNodes.forEach(node => {
        const name = node.querySelector('.tree-param-name').value.trim();
        if (!name) return;
        
        const propDef = buildPropertyFromNode(node);
        properties[name] = propDef;
        
        const isRequired = node.querySelector('.tree-param-required').checked;
        if (isRequired) {
            required.push(name);
        }
    });
    
    return {
        type: 'object',
        properties: properties,
        required: required
    };
}

// Helper function to build paramData from JSON Schema property definition
function buildParamDataFromProperty(name, propDef, requiredList) {
    const hasEnum = propDef.enum && propDef.enum.length > 0;
    const paramData = {
        name: name,
        type: hasEnum ? 'enum' : (propDef.type || 'string'),
        description: propDef.description || '',
        required: requiredList.includes(name),
        enum: propDef.enum ? propDef.enum.join(',') : '',
        default: propDef.default !== undefined ? JSON.stringify(propDef.default) : '',
        children: [],
        itemsType: 'string',
        arrayValue: '' // CSV形式の配列値
    };
    
    // Handle array items type
    if (propDef.type === 'array' && propDef.items) {
        paramData.itemsType = propDef.items.type || 'string';
        
        // const制約がある場合、配列値を適切な形式に変換
        if (propDef.const !== undefined && Array.isArray(propDef.const)) {
            if (propDef.items.type === 'object') {
                // object配列の場合、各オブジェクトをカンマ区切りで連結（[]なし）
                const objectStrings = propDef.const.map(obj => JSON.stringify(obj));
                paramData.arrayObjectValue = objectStrings.join(',\n');
            } else {
                // プリミティブ型配列の場合、CSV文字列として保存
                paramData.arrayValue = propDef.const.join(', ');
            }
        }
        
        // Handle array items with object type that have properties
        if (propDef.items.type === 'object' && propDef.items.properties) {
            const itemRequired = propDef.items.required || [];
            paramData.itemsProperties = Object.entries(propDef.items.properties).map(([itemPropName, itemPropDef]) => {
                return buildParamDataFromProperty(itemPropName, itemPropDef, itemRequired);
            });
        }
    }
    
    // Handle nested object properties
    if (propDef.type === 'object' && propDef.properties) {
        const childRequired = propDef.required || [];
        paramData.children = Object.entries(propDef.properties).map(([childName, childProp]) => {
            return buildParamDataFromProperty(childName, childProp, childRequired);
        });
    }
    
    return paramData;
}

function buildPropertyFromNode(node) {
    const type = node.querySelector('.tree-param-type').value;
    const description = node.querySelector('.tree-param-description').value.trim();
    const defaultValue = node.querySelector('.tree-param-default').value.trim();
    const enumValue = node.querySelector('.tree-param-enum').value.trim();
    
    const propDef = {};
    
    if (type === 'enum') {
        propDef.type = 'string';
        if (enumValue) {
            propDef.enum = enumValue.split(',').map(v => v.trim()).filter(v => v);
        }
    } else if (type === 'array') {
        propDef.type = 'array';
        const itemsType = node.querySelector('.tree-array-items-type').value;
        propDef.items = { type: itemsType };
        
        // If array items type is object, collect properties from array-item-properties container
        if (itemsType === 'object') {
            const arrayItemPropertiesContainer = node.querySelector('.tree-array-item-properties');
            const itemPropertyNodes = Array.from(arrayItemPropertiesContainer.children).filter(child => child.classList.contains('tree-node'));
            const itemProperties = {};
            const itemRequired = [];
            
            itemPropertyNodes.forEach(itemPropNode => {
                const childName = itemPropNode.querySelector('.tree-param-name').value.trim();
                if (!childName) return;
                
                const childPropDef = buildPropertyFromNode(itemPropNode);
                itemProperties[childName] = childPropDef;
                
                const isRequired = itemPropNode.querySelector('.tree-param-required').checked;
                if (isRequired) {
                    itemRequired.push(childName);
                }
            });
            
            if (Object.keys(itemProperties).length > 0) {
                propDef.items.properties = itemProperties;
                if (itemRequired.length > 0) {
                    propDef.items.required = itemRequired;
                }
            }
        }
        
        // If items type is object, we would need nested structure (future enhancement)
        // For now, keep it simple
    } else if (type === 'object') {
        propDef.type = 'object';
        
        // Recursively build properties from children
        const childrenContainer = node.querySelector('.tree-children');
        const childNodes = Array.from(childrenContainer.children).filter(child => child.classList.contains('tree-node'));
        
        const childProperties = {};
        const childRequired = [];
        
        childNodes.forEach(childNode => {
            const childName = childNode.querySelector('.tree-param-name').value.trim();
            if (!childName) return;
            
            childProperties[childName] = buildPropertyFromNode(childNode);
            
            const isRequired = childNode.querySelector('.tree-param-required').checked;
            if (isRequired) {
                childRequired.push(childName);
            }
        });
        
        if (Object.keys(childProperties).length > 0) {
            propDef.properties = childProperties;
        }
        if (childRequired.length > 0) {
            propDef.required = childRequired;
        }
    } else {
        propDef.type = type;
    }
    
    if (description) {
        propDef.description = description;
    }
    
    if (defaultValue) {
        try {
            propDef.default = JSON.parse(defaultValue);
        } catch {
            propDef.default = defaultValue;
        }
    }
    
    return propDef;
}

async function loadCapability() {
    const response = await fetch(`/api/capabilities/${capabilityId}`);
    const cap = await response.json();
    
    console.log('=== Capability Data ===');
    console.log('Full capability:', cap);
    console.log('Headers:', cap.headers);
    console.log('Body params:', cap.body_params);
    console.log('=====================');
    
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
        // Check if body_params has JSON Schema structure (properties field)
        const hasSchema = cap.body_params && cap.body_params.properties;
        
        if (hasSchema) {
            // New format: JSON Schema with _fixed params
            const fixedParams = cap.body_params._fixed || {};
            const properties = cap.body_params.properties || {};
            const required = cap.body_params.required || [];
            
            // Load fixed parameters
            if (Object.keys(fixedParams).length === 0 && !isMcpType) {
                addFixedParamRow('', '', isMcpType);
            } else {
                Object.entries(fixedParams).forEach(([key, valueOrObj]) => {
                    // 新形式: {value: "...", type: "..."} または旧形式: 直接値
                    const value = (typeof valueOrObj === 'object' && valueOrObj.value !== undefined) 
                        ? valueOrObj.value 
                        : valueOrObj;
                    addFixedParamRow(key, value, isMcpType);
                });
            }
            
            // Load LLM parameters from schema
            if (Object.keys(properties).length === 0 && !isMcpType) {
                addLlmParamRow(null, isMcpType);
            } else {
                Object.entries(properties).forEach(([name, propDef]) => {
                    // Check if it has enum to determine type
                    const hasEnum = propDef.enum && propDef.enum.length > 0;
                    const paramData = {
                        name: name,
                        type: hasEnum ? 'enum' : (propDef.type || 'string'),
                        description: propDef.description || '',
                        required: required.includes(name),
                        enum: propDef.enum ? propDef.enum.join(',') : '',
                        default: propDef.default !== undefined ? JSON.stringify(propDef.default) : ''
                    };
                    addLlmParamRow(paramData, isMcpType);
                });
            }
        } else {
            // Old format: simple key-value pairs - convert to new format
            const fixedParams = cap.body_params || {};
            
            if (Object.keys(fixedParams).length === 0) {
                if (!isMcpType) {
                    addFixedParamRow('', '', isMcpType);
                    addLlmParamRow(null, isMcpType);
                }
            } else {
                // Treat all existing params as fixed params for backward compatibility
                Object.entries(fixedParams).forEach(([key, value]) => {
                    addFixedParamRow(key, value, isMcpType);
                });
                if (!isMcpType) {
                    addLlmParamRow(null, isMcpType);
                }
            }
        }
    } else {
        // POST method: load into hierarchical tree editor
        
        // body_paramsが文字列の場合はパース
        let bodyParamsObj = cap.body_params;
        if (typeof bodyParamsObj === 'string') {
            try {
                bodyParamsObj = JSON.parse(bodyParamsObj);
            } catch (e) {
                console.error('Failed to parse body_params:', e);
                bodyParamsObj = {};
            }
        }
        
        const hasSchema = bodyParamsObj && bodyParamsObj.properties;
        
        console.log('POST method loading - bodyParamsObj:', bodyParamsObj);
        console.log('hasSchema:', hasSchema);
        
        if (hasSchema) {
            // New format: JSON Schema with hierarchical structure
            const fixedParams = bodyParamsObj._fixed || {};
            const properties = bodyParamsObj.properties || {};
            const required = bodyParamsObj.required || [];
            
            // Load fixed parameters
            if (Object.keys(fixedParams).length === 0 && !isMcpType) {
                // Empty fixed params - add placeholder if needed
            } else {
                Object.entries(fixedParams).forEach(([key, valueOrObj]) => {
                    let paramData;
                    if (typeof valueOrObj === 'object' && valueOrObj.schema) {
                        // 新形式: 階層構造あり
                        paramData = buildParamDataFromProperty(key, valueOrObj.schema, []);
                        paramData.default = valueOrObj.value || '';
                    } else if (typeof valueOrObj === 'object' && valueOrObj.value !== undefined) {
                        // 中間形式: {value: "...", type: "string"}
                        paramData = {
                            name: key,
                            type: valueOrObj.type || 'string',
                            default: valueOrObj.value,
                            description: '',
                            required: false,
                            enum: '',
                            children: [],
                            itemsType: 'string'
                        };
                    } else {
                        // 旧形式互換: 直接値
                        paramData = {
                            name: key,
                            type: 'string',
                            default: valueOrObj,
                            description: '',
                            required: false,
                            enum: '',
                            children: [],
                            itemsType: 'string'
                        };
                    }
                    addFixedParamPostRow(null, 0, paramData, isMcpType);
                });
            }
            
            // Load LLM parameters into tree structure
            if (Object.keys(properties).length === 0 && !isMcpType) {
                addLlmParamTreeRow(null, 0);
            } else {
                Object.entries(properties).forEach(([name, propDef]) => {
                    const paramData = buildParamDataFromProperty(name, propDef, required);
                    addLlmParamTreeRow(null, 0, paramData);
                });
            }
        } else {
            // Old format: convert to tree structure
            // This is the old format where each parameter has {type, description, required}
            if (bodyParamsObj && Object.keys(bodyParamsObj).length > 0) {
                Object.entries(bodyParamsObj).forEach(([key, paramDef]) => {
                    // Check if it's the old format with type/description/required
                    if (paramDef && typeof paramDef === 'object' && paramDef.type) {
                        const paramData = {
                            name: key,
                            type: paramDef.type || 'string',
                            description: paramDef.description || '',
                            required: paramDef.required || false,
                            enum: '',
                            default: '',
                            children: [],
                            itemsType: 'string'
                        };
                        addLlmParamTreeRow(null, 0, paramData);
                    } else {
                        // Even older format: just key-value pairs
                        const paramData = {
                            name: key,
                            type: typeof paramDef === 'number' ? 'number' : typeof paramDef === 'boolean' ? 'boolean' : 'string',
                            default: paramDef,
                            description: '',
                            required: false,
                            enum: '',
                            children: [],
                            itemsType: 'string'
                        };
                        addFixedParamPostRow(null, 0, paramData, isMcpType);
                    }
                });
            } else if (!isMcpType) {
                // No params - add empty row
                addLlmParamTreeRow(null, 0);
            }
        }
    }
    
    // Hide "Add" buttons for MCP type
    if (isMcpType) {
        const addFixedBtn = document.querySelector('button[onclick="addFixedParamRow()"]');
        if (addFixedBtn) addFixedBtn.style.display = 'none';
        const addLlmBtn = document.querySelector('button[onclick="addLlmParamRow()"]');
        if (addLlmBtn) addLlmBtn.style.display = 'none';
        
        // Hide POST editor buttons
        const addFixedPostBtn = document.querySelector('button[onclick="addFixedParamPostRow()"]');
        if (addFixedPostBtn) addFixedPostBtn.style.display = 'none';
        const addLlmTreeBtn = document.querySelector('button[onclick*="addLlmParamTreeRow"]');
        if (addLlmTreeBtn) addLlmTreeBtn.style.display = 'none';
    }
    
    return isMcpType;
}

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    const isMcpType = await loadCapability();
    await loadPermissions();
    
    // Setup auto-update for request sample (debounced)
    let sampleUpdateTimer;
    function scheduleRequestSampleUpdate() {
        clearTimeout(sampleUpdateTimer);
        sampleUpdateTimer = setTimeout(() => {
            generateRequestSample();
        }, 500); // 500ms debounce
    }
    
    // Listen to method changes
    document.getElementById('method').addEventListener('change', () => {
        toggleBodyType();
        scheduleRequestSampleUpdate();
    });
    
    // Listen to URL changes
    document.getElementById('url').addEventListener('input', scheduleRequestSampleUpdate);
    
    // Use event delegation for dynamically added parameter rows
    document.addEventListener('input', (e) => {
        // Check if the input is in parameter containers
        if (e.target.closest('#fixed-params-container') ||
            e.target.closest('#llm-params-container') ||
            e.target.closest('#fixed-params-post-container') ||
            e.target.closest('#llm-params-tree-container')) {
            scheduleRequestSampleUpdate();
        }
    });
    
    // Listen to checkbox changes in parameter rows
    document.addEventListener('change', (e) => {
        if (e.target.closest('#llm-params-container') ||
            e.target.closest('#llm-params-tree-container')) {
            scheduleRequestSampleUpdate();
        }
    });
    
    // Initial sample generation
    setTimeout(generateRequestSample, 100);
    
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
            const properties = {};
            const required = [];
            
            // 固定パラメータをconst制約付きでpropertiesに含める
            const fixedRows = document.querySelectorAll('#fixed-params-container .key-value-row');
            fixedRows.forEach(row => {
                const inputs = row.querySelectorAll('input[type="text"]');
                const key = inputs[0].value.trim();
                const value = inputs[1].value.trim();
                if (key) {
                    // GET固定パラメータはstring型のconst制約
                    properties[key] = {
                        type: 'string',
                        const: value,
                        default: value,
                        description: '固定値パラメータ（変更不可）'
                    };
                    required.push(key);
                }
            });
            
            // Collect LLM parameters and build JSON Schema
            const llmRows = document.querySelectorAll('#llm-params-container .llm-param-row');
            
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
                // MCP JSON Schema format (固定パラメータもpropertiesに含まれている)
                bodyParams = {
                    type: 'object',
                    properties: properties,
                    required: required
                };
            }
        } else {
            // POST method: always use visual editor mode
            bodyParams = buildSchemaFromTree();
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
// Cache bust: 2025-12-05T00:00:00
