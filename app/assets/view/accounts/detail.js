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
            <div class="token-display" style="display: flex; gap: 10px; align-items: center;">
                <code style="flex: 1; padding: 10px; background: #f5f5f5; border-radius: 4px; overflow-x: auto;">${account.bearer_token}</code>
                <button onclick="copyToken('${account.bearer_token}')" class="btn btn-sm btn-secondary">${t('account_copy_token')}</button>
                <button onclick="regenerateToken()" class="btn btn-sm btn-warning">${t('account_regenerate_token')}</button>
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

function copyToken(token) {
    navigator.clipboard.writeText(token);
    alert(t('account_token_copied'));
}

async function regenerateToken() {
    if (!confirm(t('account_regenerate_confirm'))) return;
    
    try {
        const response = await fetch(`/api/accounts/${accountId}/regenerate_token`, { method: 'POST' });
        if (response.ok) {
            alert(t('account_token_regenerated'));
            await loadAccount();
        } else {
            alert('トークンの再発行に失敗しました');
        }
    } catch (error) {
        console.error('Error regenerating token:', error);
        alert('トークンの再発行に失敗しました');
    }
}

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    await loadAccount();
    
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
