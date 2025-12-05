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

// ============================================
// POST Method: Hierarchical Tree Editor
// ============================================

// Fixed Parameters for POST
let fixedParamPostIndex = 0;
function addFixedParamPostRow(key = '', value = '', isReadOnly = false) {
    const container = document.getElementById('fixed-params-post-container');
    const index = fixedParamPostIndex++;
    
    const readOnlyStyle = isReadOnly ? 'background-color: #f5f5f5; cursor: not-allowed;' : '';
    const readOnlyAttr = isReadOnly ? 'readonly disabled' : '';
    
    const row = document.createElement('div');
    row.className = 'key-value-row';
    row.setAttribute('data-index', index);
    row.style.cssText = 'display: flex; gap: 10px; margin-bottom: 10px; align-items: center;';
    row.innerHTML = `
        <input type="text" class="fixed-param-post-key" placeholder="key" value="${key}" ${readOnlyAttr}
               style="flex: 1; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; ${readOnlyStyle}">
        <input type="text" class="fixed-param-post-value" placeholder="value or {{VARIABLE_NAME}}" value="${value}" ${readOnlyAttr}
               style="flex: 1; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; ${readOnlyStyle}">
        ${!isReadOnly ? `<button type="button" onclick="this.closest('.key-value-row').remove()" class="btn btn-sm btn-danger">削除</button>` : ''}
    `;
    container.appendChild(row);
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
    } else if (containerOrParent.id === 'llm-params-tree-container') {
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
        <div class="tree-node-header" style="display: flex; gap: 10px; align-items: start; margin-bottom: 8px;">
            <button type="button" class="expand-btn" onclick="toggleTreeNode(${nodeId})" 
                    style="width: 24px; height: 24px; border: none; background: #f0f0f0; border-radius: 4px; cursor: pointer; font-size: 0.8rem; display: ${isExpandable ? 'block' : 'none'};">
                ${expandIcon}
            </button>
            <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr 2fr auto; gap: 8px; align-items: start;">
                <div>
                    <input type="text" class="tree-param-name" value="${data.name}" placeholder="param_name"
                           style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                </div>
                <div>
                    <select class="tree-param-type" onchange="handleTreeTypeChange(${nodeId})" 
                            style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                        <option value="string" ${data.type === 'string' ? 'selected' : ''}>string</option>
                        <option value="number" ${data.type === 'number' ? 'selected' : ''}>number</option>
                        <option value="integer" ${data.type === 'integer' ? 'selected' : ''}>integer</option>
                        <option value="boolean" ${data.type === 'boolean' ? 'selected' : ''}>boolean</option>
                        <option value="enum" ${data.type === 'enum' ? 'selected' : ''}>enum</option>
                        <option value="object" ${data.type === 'object' ? 'selected' : ''}>object</option>
                        <option value="array" ${data.type === 'array' ? 'selected' : ''}>array</option>
                    </select>
                </div>
                <div>
                    <input type="text" class="tree-param-description" value="${data.description}" placeholder="説明"
                           style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
                </div>
                <div style="display: flex; gap: 6px; align-items: center;">
                    <label title="必須" style="display: flex; align-items: center; cursor: pointer;">
                        <input type="checkbox" class="tree-param-required" ${data.required ? 'checked' : ''}
                               style="width: 16px; height: 16px; margin: 0;">
                    </label>
                    <button type="button" onclick="removeTreeNode(${nodeId})" class="btn btn-sm btn-danger" style="padding: 4px 8px; font-size: 0.8rem;">×</button>
                </div>
            </div>
        </div>
        
        <!-- Enum values field (shown when type is enum) -->
        <div class="tree-enum-field" style="display: ${data.type === 'enum' ? 'block' : 'none'}; margin-bottom: 8px; margin-left: 34px;">
            <input type="text" class="tree-param-enum" value="${data.enum}" placeholder="option1,option2,option3"
                   style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
            <small style="display: block; color: #6c757d; font-size: 0.75rem; margin-top: 2px;">カンマ区切りで選択肢を入力</small>
        </div>
        
        <!-- Default value field -->
        <div class="tree-default-field" style="margin-bottom: 8px; margin-left: 34px;">
            <input type="text" class="tree-param-default" value="${data.default}" placeholder="デフォルト値"
                   style="width: 100%; padding: 6px 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem;">
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
        
        <!-- Children container (for object type) -->
        <div class="tree-children" style="display: ${isExpandable && hasChildren ? 'block' : 'none'}; margin-left: 20px; margin-top: 10px;"></div>
        
        <!-- Add child button (for object type) -->
        <div class="tree-add-child" style="display: ${data.type === 'object' ? 'block' : 'none'}; margin-left: 34px; margin-top: 8px;">
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
    
    // Show/hide fields based on type
    enumField.style.display = selectedType === 'enum' ? 'block' : 'none';
    arrayItemsField.style.display = selectedType === 'array' ? 'block' : 'none';
    addChildBtn.style.display = selectedType === 'object' ? 'block' : 'none';
    expandBtn.style.display = selectedType === 'object' ? 'block' : 'none';
    
    // Array items object control
    if (selectedType === 'array') {
        const itemsType = node.querySelector('.tree-array-items-type').value;
        addArrayItemPropertyBtn.style.display = itemsType === 'object' ? 'block' : 'none';
    } else {
        addArrayItemPropertyBtn.style.display = 'none';
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
    
    addArrayItemPropertyBtn.style.display = itemsType === 'object' ? 'block' : 'none';
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

// Build JSON Schema from tree structure
function buildSchemaFromTree() {
    const treeContainer = document.getElementById('llm-params-tree-container');
    const rootNodes = Array.from(treeContainer.children).filter(child => child.classList.contains('tree-node'));
    
    const properties = {};
    const required = [];
    
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
        itemsType: 'string'
    };
    
    // Handle array items type
    if (propDef.type === 'array' && propDef.items) {
        paramData.itemsType = propDef.items.type || 'string';
        
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

// Toggle between visual editor and JSON direct edit
function toggleBodyEditorMode() {
    const useAdvancedMode = document.getElementById('use-advanced-mode').checked;
    const visualEditor = document.getElementById('visual-editor');
    const jsonEditor = document.getElementById('json-editor');
    const bodyJsonTextarea = document.getElementById('body_json');
    
    if (useAdvancedMode) {
        // Switching to JSON mode: build JSON from tree and populate textarea
        const fixedParams = {};
        const fixedRows = document.querySelectorAll('#fixed-params-post-container .key-value-row');
        fixedRows.forEach(row => {
            const key = row.querySelector('.fixed-param-post-key').value.trim();
            const value = row.querySelector('.fixed-param-post-value').value.trim();
            if (key) {
                fixedParams[key] = value;
            }
        });
        
        const schema = buildSchemaFromTree();
        
        const fullSchema = {
            ...schema,
            _fixed: fixedParams
        };
        
        bodyJsonTextarea.value = JSON.stringify(fullSchema, null, 2);
        visualEditor.style.display = 'none';
        jsonEditor.style.display = 'block';
    } else {
        // Switching to visual mode: parse JSON and rebuild tree (optional: could show warning)
        // For now, just switch the display
        visualEditor.style.display = 'block';
        jsonEditor.style.display = 'none';
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
                Object.entries(fixedParams).forEach(([key, value]) => {
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
        const hasSchema = cap.body_params && cap.body_params.properties;
        
        if (hasSchema) {
            // New format: JSON Schema with hierarchical structure
            const fixedParams = cap.body_params._fixed || {};
            const properties = cap.body_params.properties || {};
            const required = cap.body_params.required || [];
            
            // Load fixed parameters
            if (Object.keys(fixedParams).length === 0 && !isMcpType) {
                addFixedParamPostRow('', '', isMcpType);
            } else {
                Object.entries(fixedParams).forEach(([key, value]) => {
                    addFixedParamPostRow(key, value, isMcpType);
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
            // Old format or no schema: show in JSON editor (advanced mode)
            document.getElementById('use-advanced-mode').checked = true;
            toggleBodyEditorMode();
        }
        
        // Also populate JSON textarea for advanced mode
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
            // POST method: check if using visual editor or JSON direct edit
            const useAdvancedMode = document.getElementById('use-advanced-mode').checked;
            
            if (!useAdvancedMode) {
                // Visual editor mode: build from tree structure
                const fixedParams = {};
                const fixedRows = document.querySelectorAll('#fixed-params-post-container .key-value-row');
                fixedRows.forEach(row => {
                    const key = row.querySelector('.fixed-param-post-key').value.trim();
                    const value = row.querySelector('.fixed-param-post-value').value.trim();
                    if (key) {
                        fixedParams[key] = value;
                    }
                });
                
                const schema = buildSchemaFromTree();
                
                bodyParams = {
                    ...schema,
                    _fixed: fixedParams
                };
            } else {
                // JSON direct edit mode
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
