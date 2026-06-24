// accounts/list.js - Accounts List Page

async function loadAccounts() {
    const response = await fetch('/api/accounts');
    const allAccounts = await response.json();

    // システムアカウントは接続ガイドページで管理するため一覧から除外
    const accounts = allAccounts.filter(a => !a.is_system);

    const container = document.getElementById('accounts-list');
    
    if (accounts.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('account_empty')}</div>`;
        return;
    }
    
    container.innerHTML = accounts.map(account => `
        <div class="list-item">
            <div class="list-item-main">
                <h3>
                    <a href="/accounts/${account.id}">${account.name}</a>
                    ${account.is_system ? '<span class="badge badge-system" title="システムアカウント（削除不可）">&#128274; システム</span>' : ''}
                </h3>
                <div class="list-item-meta">
                    ${account.notes ? `<span class="text-muted">${account.notes.substring(0, 50)}${account.notes.length > 50 ? '...' : ''}</span>` : ''}
                    <span class="text-muted">${t('account_created')}: ${new Date(account.created_at).toLocaleDateString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</span>
                </div>
            </div>
            <div class="list-item-actions">
                ${account.is_system
                    ? ''
                    : `<button onclick="deleteAccount(${account.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>`
                }
            </div>
        </div>
    `).join('');
}

async function deleteAccount(id) {
    const confirmed = await modal.confirmDelete(t('account_delete_confirm'));
    if (!confirmed) return;
    
    await fetch(`/api/accounts/${id}`, { method: 'DELETE' });
    loadAccounts();
}

// Initialize language and load accounts
(async () => {
    await initLanguageSwitcher();
    loadAccounts();
})();

