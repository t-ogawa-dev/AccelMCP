// admin_users/detail.js - Admin User Detail/Edit Page
const adminUserId = parseInt(window.location.pathname.split('/')[2]);

async function loadAdminUser() {
    const response = await fetch(`/api/admin-users/${adminUserId}`);
    const user = await response.json();

    document.getElementById('username').value = user.username;

    const container = document.getElementById('admin-user-detail');
    container.innerHTML = `
        <div class="detail-section">
            <h2>${user.username}</h2>
            ${!user.is_initialized ? `<p class="text-muted">${t('admin_user_pending_change_desc')}</p>` : ''}
        </div>
        <div class="detail-section">
            <table class="detail-table">
                <tr>
                    <th>${t('account_created_at')}</th>
                    <td>${new Date(user.created_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
                <tr>
                    <th>${t('account_updated_at')}</th>
                    <td>${new Date(user.updated_at).toLocaleString(currentLanguage === 'ja' ? 'ja-JP' : 'en-US')}</td>
                </tr>
            </table>
        </div>
    `;
}

async function deleteAdminUserSelf() {
    const confirmed = await modal.confirmDelete(t('admin_user_delete_confirm'));
    if (!confirmed) return;

    const response = await fetch(`/api/admin-users/${adminUserId}`, { method: 'DELETE' });
    if (response.ok) {
        window.location.href = '/admin-users';
    } else {
        const error = await response.json().catch(() => ({}));
        await modal.error(error.error || t('admin_user_delete_failed'));
    }
}

(async () => {
    await initLanguageSwitcher();
    await loadAdminUser();

    document.getElementById('edit-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = { username: formData.get('username').trim() };
        const password = formData.get('password');
        if (password) {
            if (password.length < 8) {
                await modal.error(t('admin_user_pw_too_short'));
                return;
            }
            data.password = password;
        }

        const response = await fetch(`/api/admin-users/${adminUserId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            await modal.success(t('admin_user_update_success'));
            document.getElementById('password').value = '';
            loadAdminUser();
        } else {
            const error = await response.json();
            await modal.error(t('admin_user_update_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });

    document.getElementById('delete-btn').addEventListener('click', deleteAdminUserSelf);
})();
