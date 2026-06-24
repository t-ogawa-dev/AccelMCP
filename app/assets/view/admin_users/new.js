// admin_users/new.js - New Admin User Registration Page

(async () => {
    await initLanguageSwitcher();

    document.getElementById('admin-user-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);
        const username = formData.get('username').trim();
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');

        if (password !== confirmPassword) {
            await modal.error(t('admin_user_pw_mismatch'));
            return;
        }
        if (password.length < 8) {
            await modal.error(t('admin_user_pw_too_short'));
            return;
        }

        const response = await fetch('/api/admin-users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            window.location.href = '/admin-users';
        } else {
            const error = await response.json();
            await modal.error(t('admin_user_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
