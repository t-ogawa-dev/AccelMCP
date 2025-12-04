// services/new.js - Service Registration Page
let headerIndex = 0;

function toggleServiceType() {
    const serviceType = document.querySelector('input[name="service_type"]:checked').value;
    const mcpUrlSection = document.getElementById('mcp-url-section');
    const mcpUrlInput = document.getElementById('mcp_url');
    
    if (serviceType === 'mcp') {
        mcpUrlSection.style.display = 'block';
        mcpUrlInput.setAttribute('required', 'required');
    } else {
        mcpUrlSection.style.display = 'none';
        mcpUrlInput.removeAttribute('required');
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

async function testConnection() {
    const mcpUrl = document.getElementById('mcp_url').value.trim();
    const resultDiv = document.getElementById('connection-test-result');
    
    if (!mcpUrl) {
        resultDiv.style.display = 'block';
        resultDiv.style.padding = '12px';
        resultDiv.style.borderRadius = '6px';
        resultDiv.style.backgroundColor = '#fee';
        resultDiv.style.border = '1px solid #fcc';
        resultDiv.style.color = '#c33';
        resultDiv.textContent = t('app_mcp_url_required') || 'MCP接続URLを入力してください';
        return false;
    }
    
    // Collect common headers
    const commonHeaders = {};
    const headerRows = document.querySelectorAll('#headers-container .key-value-row');
    headerRows.forEach(row => {
        const inputs = row.querySelectorAll('input[type="text"]');
        const key = inputs[0].value.trim();
        const value = inputs[1].value.trim();
        if (key) {
            commonHeaders[key] = value;
        }
    });
    
    // Show loading state
    resultDiv.style.display = 'block';
    resultDiv.style.padding = '12px';
    resultDiv.style.borderRadius = '6px';
    resultDiv.style.backgroundColor = '#f0f9ff';
    resultDiv.style.border = '1px solid #bae6fd';
    resultDiv.style.color = '#0369a1';
    resultDiv.textContent = t('app_testing_connection') || '接続テスト中...';
    
    try {
        const response = await fetch('/api/apps/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                mcp_url: mcpUrl,
                common_headers: commonHeaders
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Success
            resultDiv.style.backgroundColor = '#d1fae5';
            resultDiv.style.border = '1px solid #10b981';
            resultDiv.style.color = '#065f46';
            resultDiv.textContent = '✓ ' + (t('app_connection_success') || '接続成功');
            return true;
        } else {
            // Failure
            resultDiv.style.backgroundColor = '#fee';
            resultDiv.style.border = '1px solid #fcc';
            resultDiv.style.color = '#c33';
            resultDiv.textContent = '✗ ' + (result.error || t('app_connection_failed') || '接続失敗');
            return false;
        }
    } catch (e) {
        // Error
        resultDiv.style.backgroundColor = '#fee';
        resultDiv.style.border = '1px solid #fcc';
        resultDiv.style.color = '#c33';
        resultDiv.textContent = '✗ ' + (t('app_connection_error') || '接続エラー') + ': ' + e.message;
        return false;
    }
}

// Initialize and setup form
(async () => {
    await initLanguageSwitcher();
    
    // URLからMCPサービスIDを取得
    const pathParts = window.location.pathname.split('/');
    const mcpServiceId = pathParts[2]; // /mcp-services/{id}/apps/new
    
    if (!mcpServiceId) {
        console.error('MCP Service ID not found in URL');
        alert('MCPサービスIDが見つかりません');
        window.location.href = '/mcp-services';
        return;
    }
    
    // Check for template data in sessionStorage
    const templateDataStr = sessionStorage.getItem('app_template_data');
    if (templateDataStr) {
        try {
            const templateData = JSON.parse(templateDataStr);
            
            // Fill form with template data
            if (templateData.name) {
                document.getElementById('name').value = templateData.name;
            }
            if (templateData.description) {
                document.getElementById('description').value = templateData.description;
            }
            if (templateData.service_type) {
                document.querySelector(`input[name="service_type"][value="${templateData.service_type}"]`).checked = true;
                toggleServiceType();
            }
            if (templateData.mcp_url) {
                document.getElementById('mcp_url').value = templateData.mcp_url;
            }
            
            // Fill common headers
            if (templateData.common_headers && Object.keys(templateData.common_headers).length > 0) {
                // Clear default header row
                document.getElementById('headers-container').innerHTML = '';
                
                // Add headers from template
                Object.entries(templateData.common_headers).forEach(([key, value]) => {
                    addHeaderRow(key, value);
                });
            } else {
                // Add initial empty header row
                addHeaderRow();
            }
            
            // Show info message
            if (templateData.official_url) {
                const infoDiv = document.createElement('div');
                infoDiv.style.cssText = 'margin-bottom: 20px; padding: 12px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; color: #0369a1;';
                infoDiv.innerHTML = `
                    📚 テンプレートから作成中: ${templateData.name}<br>
                    <a href="${templateData.official_url}" target="_blank" style="color: #0369a1; text-decoration: underline;">公式ドキュメント</a>
                `;
                document.querySelector('form').insertBefore(infoDiv, document.querySelector('form').firstChild);
            }
            
            // Clear template data from sessionStorage
            sessionStorage.removeItem('app_template_data');
        } catch (e) {
            console.error('Failed to parse template data:', e);
        }
    } else {
        // Add initial header row if no template data
        addHeaderRow();
    }
    
    // Setup form submit handler
    document.getElementById('service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const serviceType = formData.get('service_type');
        
        // For MCP type, validate connection first
        if (serviceType === 'mcp') {
            const connectionSuccess = await testConnection();
            if (!connectionSuccess) {
                alert(t('app_mcp_connection_required') || 'MCP接続テストに成功してから登録してください');
                return;
            }
        }
        
        const data = {
            name: formData.get('name'),
            description: formData.get('description'),
            service_type: serviceType,
            common_headers: {},
            mcp_service_id: mcpServiceId
        };
        
        if (serviceType === 'mcp') {
            data.mcp_url = formData.get('mcp_url');
        }
        
        // Collect headers for both API and MCP types
        const headerRows = document.querySelectorAll('#headers-container .key-value-row');
        headerRows.forEach(row => {
            const inputs = row.querySelectorAll('input[type="text"]');
            const key = inputs[0].value.trim();
            const value = inputs[1].value.trim();
            if (key) {
                data.common_headers[key] = value;
            }
        });
        
        const response = await fetch('/api/apps', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = `/mcp-services/${mcpServiceId}/apps`;
        } else {
            const error = await response.json();
            alert(t('app_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
