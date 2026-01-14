// accounts/new.js - New Account Registration Page

// Initialize and setup
(async () => {
    await initLanguageSwitcher();
    
    // Setup form submit handler
    document.getElementById('account-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            name: formData.get('username'),
            notes: formData.get('notes')
        };
        
        const response = await fetch('/api/accounts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = '/accounts';
        } else {
            const error = await response.json();
            await modal.error(t('account_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    });
})();
