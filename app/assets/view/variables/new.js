/**
 * Variable新規登録画面
 */

document.getElementById('variable-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        name: document.getElementById('name').value.toUpperCase(),
        value: document.getElementById('value').value,
        value_type: document.querySelector('input[name="value_type"]:checked').value,
        description: document.getElementById('description').value,
        is_secret: document.getElementById('is_secret').checked
    };
    
    try {
        const response = await fetch('/api/variables', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = '/variables';
        } else {
            const error = await response.json();
            alert(t('variable_register_failed') + ': ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        alert(t('variable_register_failed') + ': ' + error.message);
    }
});

// 言語初期化
(async () => {
    await initLanguageSwitcher();
})();
