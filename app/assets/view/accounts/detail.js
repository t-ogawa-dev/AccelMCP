// accounts/detail.js - Account Detail Page
const accountId = parseInt(window.location.pathname.split('/')[2]);
let allServices = [];
let allCapabilities = [];

async function loadAccount() {
    const response = await fetch(`/api/accounts/${accountId}`);
    const account = await response.json();
    
    document.getElementById('name').value = account.name;
    document.getElementById('notes').value = account.notes || '';
    
    const container = document.getElementById('account-detail');
    container.innerHTML = `
        <div class="detail-section">
            <h2>${account.name}</h2>
        </div>
        
        <div class="detail-section">
            <h3>${t('account_bearer_token')}</h3>
            <div class="token-display">
                <code>${account.bearer_token}</code>
                <button onclick="copyToken('${account.bearer_token}')" class="btn btn-sm">${t('account_copy_token')}</button>
            </div>
        </div>
        
        ${account.notes ? `
        <div class="detail-section">
            <h3>${t('account_notes_label')}</h3>
            <p style="white-space: pre-wrap;">${account.notes}</p>
        </div>
        ` : ''}
        
        <div class="detail-section">
            <table class="detail-table">
                <tr>
                    <th>${t('account_created_at')}</th>
                    <td>${new Date(account.created_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
                <tr>
                    <th>${t("account_updated_at")}</th>
                    <td>${new Date(account.updated_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
            </table>
        </div>
    `;
}

async function loadPermissions() {
    const response = await fetch(`/api/accounts/${accountId}/permissions`);
    const permissions = await response.json();
    
    const container = document.getElementById('permissions-list');
    
    if (permissions.length === 0) {
        container.innerHTML = `<p class="text-muted">${t('account_no_capabilities')}</p>`;
        return;
    }
    
    // Group by service
    const serviceMap = {};
    permissions.forEach(perm => {
        const serviceName = perm.capability.service_name || t('account_unknown_service');
        if (!serviceMap[serviceName]) {
            serviceMap[serviceName] = [];
        }
        serviceMap[serviceName].push(perm.capability);
    });
    
    let html = '';
    for (const [serviceName, capabilities] of Object.entries(serviceMap)) {
        html += `
            <div class="service-section" style="margin-bottom: 20px;">
                <h4 style="margin-bottom: 10px;">${serviceName}</h4>
                <div class="permissions-grid">
                    ${capabilities.map(cap => `
                        <div class="permission-item">
                            <div>
                                <strong>${cap.name}</strong>
                                <span class="badge badge-${cap.capability_type || cap.type}">${(cap.capability_type || cap.type || 'tool').toUpperCase()}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function copyToken(token) {
    navigator.clipboard.writeText(token);
    alert(t('account_token_copied'));
}

async function regenerateToken() {
    if (!confirm(t('account_regenerate_confirm'))) return;
    
    await fetch(`/api/accounts/${accountId}/regenerate_token`, { method: 'POST' });
    loadAccount();
    alert(t('account_token_regenerated'));
}

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    await loadAccount();
    await loadPermissions();
    
    // Setup form submit handler
    document.getElementById('edit-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            notes: formData.get('notes')
        };
        
        const response = await fetch(`/api/accounts/${accountId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert(t('account_update_success'));
            loadAccount();
        } else {
            const error = await response.json();
            alert(t('account_update_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
