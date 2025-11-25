// services/edit.js - Service Edit Page
const pathParts = window.location.pathname.split('/');
const mcpServiceId = parseInt(pathParts[2]); // /mcp-services/{id}/apps/{app_id}/edit
const serviceId = parseInt(pathParts[4]);
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

async function loadService() {
    const response = await fetch(`/api/apps/${serviceId}`);
    const service = await response.json();
    
    document.getElementById('name').value = service.name;
    document.getElementById('description').value = service.description || '';
    
    // Set service type
    const serviceType = service.service_type || 'api';
    document.querySelector(`input[name="service_type"][value="${serviceType}"]`).checked = true;
    
    if (serviceType === 'mcp') {
        document.getElementById('mcp_url').value = service.mcp_url || '';
    }
    
    toggleServiceType();
    
    // Load headers
    const headers = service.common_headers || {};
    if (Object.keys(headers).length === 0 && serviceType === 'api') {
        addHeaderRow(); // Add empty row if no headers
    } else {
        Object.entries(headers).forEach(([key, value]) => {
            addHeaderRow(key, value);
        });
    }
}

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    await loadService();
    
    // Setup form submit handler
    document.getElementById('service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const serviceType = formData.get('service_type');
        const data = {
            name: formData.get('name'),
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
        
        const response = await fetch(`/api/apps/${serviceId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = `/mcp-services/${mcpServiceId}/apps/${serviceId}`;
        } else {
            alert(t('app_update_failed'));
        }
    });
})();
