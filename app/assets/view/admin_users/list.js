// admin_users/list.js - Admin Users (Web Login Accounts) List Page

async function loadAdminUsers() {
    const response = await fetch('/api/admin-users');
    const users = await response.json();

    const container = document.getElementById('admin-users-list');

    if (users.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('admin_user_empty')}</div>`;
        return;
    }

    container.innerHTML = users.map(user => `
        <div class="list-item">
            <div class="list-item-main">
                <h3><a href="/admin-users/${user.id}">${user.username}</a></h3>
                <div class="list-item-meta">
                    <span class="text-muted">${t('admin_user_created')}: ${new Date(user.created_at).toLocaleDateString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</span>
                    ${!user.is_initialized ? `<span class="text-muted">（${t('admin_user_pending_change')}）</span>` : ''}
                </div>
            </div>
            <div class="list-item-actions">
                <button onclick="deleteAdminUser(${user.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>
            </div>
        </div>
    `).join('');
}

async function deleteAdminUser(id) {
    const confirmed = await modal.confirmDelete(t('admin_user_delete_confirm'));
    if (!confirmed) return;

    const response = await fetch(`/api/admin-users/${id}`, { method: 'DELETE' });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        await modal.error(error.error || t('admin_user_delete_failed'));
        return;
    }
    loadAdminUsers();
}

// Initialize language and load admin users
(async () => {
    await initLanguageSwitcher();
    loadAdminUsers();
})();
