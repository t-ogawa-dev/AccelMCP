// services/new.js - Service Registration Page
let headerIndex = 0;

function toggleServiceType() {
    const serviceType = document.querySelector('input[name="service_type"]:checked').value;
    const mcpUrlSection = document.getElementById('mcp-url-section');
    const commonHeadersSection = document.getElementById('common-headers-section');
    const mcpUrlInput = document.getElementById('mcp_url');
    
    if (serviceType === 'mcp') {
        mcpUrlSection.style.display = 'block';
        commonHeadersSection.style.display = 'none';
        mcpUrlInput.setAttribute('required', 'required');
    } else {
        mcpUrlSection.style.display = 'none';
        commonHeadersSection.style.display = 'block';
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
        return;
    }
    
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
            body: JSON.stringify({ mcp_url: mcpUrl })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Success
            resultDiv.style.backgroundColor = '#d1fae5';
            resultDiv.style.border = '1px solid #10b981';
            resultDiv.style.color = '#065f46';
            resultDiv.textContent = '✓ ' + (t('app_connection_success') || '接続成功');
        } else {
            // Failure
            resultDiv.style.backgroundColor = '#fee';
            resultDiv.style.border = '1px solid #fcc';
            resultDiv.style.color = '#c33';
            resultDiv.textContent = '✗ ' + (result.error || t('app_connection_failed') || '接続失敗');
        }
    } catch (e) {
        // Error
        resultDiv.style.backgroundColor = '#fee';
        resultDiv.style.border = '1px solid #fcc';
        resultDiv.style.color = '#c33';
        resultDiv.textContent = '✗ ' + (t('app_connection_error') || '接続エラー') + ': ' + e.message;
    }
}

// Initialize and setup form
(async () => {
    await initLanguageSwitcher();
    
    // Add initial header row
    addHeaderRow();
    
    // Setup form submit handler
    document.getElementById('service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const serviceType = formData.get('service_type');
        const data = {
            name: formData.get('name'),
            subdomain: formData.get('subdomain'),
            description: formData.get('description'),
            service_type: serviceType,
            common_headers: {}
        };
        
        if (serviceType === 'mcp') {
            data.mcp_url = formData.get('mcp_url');
        } else {
            // Collect headers
            const headerRows = document.querySelectorAll('#headers-container .key-value-row');
            headerRows.forEach(row => {
                const inputs = row.querySelectorAll('input[type="text"]');
                const key = inputs[0].value.trim();
                const value = inputs[1].value.trim();
                if (key) {
                    data.common_headers[key] = value;
                }
            });
        }
        
        const response = await fetch('/api/apps', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = '/services';
        } else {
            const error = await response.json();
            alert(t('app_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
