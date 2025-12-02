/**
 * MCPサービス編集画面
 * アクセス制御: トグルON=制限あり(restricted), OFF=制限なし(public)
 */

const mcpServiceId = parseInt(window.location.pathname.split('/')[2]);
let currentAccessControl = 'restricted'; // デフォルトはrestricted

// Update access control UI
function updateAccessControlUI(isRestricted) {
    const permissionsSection = document.getElementById('permissions-section');
    
    if (isRestricted) {
        permissionsSection.style.display = 'block';
    } else {
        permissionsSection.style.display = 'none';
    }
}

// Load MCP Service data
async function loadMcpService() {
    const response = await fetch(`/api/mcp-services/${mcpServiceId}`);
    const service = await response.json();
    
    document.getElementById('name').value = service.name;
    document.getElementById('subdomain').value = service.subdomain;
    document.getElementById('description').value = service.description || '';
    
    // Set access control
    currentAccessControl = service.access_control || 'restricted';
    const isRestricted = currentAccessControl === 'restricted';
    document.getElementById('access-control-toggle').checked = isRestricted;
    updateAccessControlUI(isRestricted);
}

// Load account permissions
async function loadPermissions() {
    const response = await fetch(`/api/mcp-services/${mcpServiceId}/permissions`);
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
    
    const response = await fetch(`/api/mcp-services/${mcpServiceId}/permissions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_ids: enabledAccountIds })
    });
    
    if (!response.ok) {
        throw new Error('Failed to save permissions');
    }
}

(async () => {
    await initLanguageSwitcher();
    await loadMcpService();
    await loadPermissions();
    
    // Access control toggle handler
    document.getElementById('access-control-toggle').addEventListener('change', async (e) => {
        const isRestricted = e.target.checked;
        updateAccessControlUI(isRestricted);
        currentAccessControl = isRestricted ? 'restricted' : 'public';
    });
    
    // Form submit handler
    document.getElementById('mcp-service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            // Update basic info
            const formData = new FormData(e.target);
            const data = {
                name: formData.get('name'),
                subdomain: formData.get('subdomain'),
                description: formData.get('description')
            };
            
            const response = await fetch(`/api/mcp-services/${mcpServiceId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || t('error_unknown'));
            }
            
            // Update access control
            const accessControlResponse = await fetch(`/api/mcp-services/${mcpServiceId}/access-control`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ access_control: currentAccessControl })
            });
            
            if (!accessControlResponse.ok) {
                throw new Error('Failed to update access control');
            }
            
            // Save permissions if restricted
            if (currentAccessControl === 'restricted') {
                await savePermissions();
            }
            
            window.location.href = `/mcp-services/${mcpServiceId}`;
        } catch (error) {
            alert(t('mcp_service_update_failed') + ': ' + error.message);
        }
    });
})();
