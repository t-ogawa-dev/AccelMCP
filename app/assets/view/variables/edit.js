/**
 * Variable編集画面
 */

const variableId = parseInt(window.location.pathname.split('/')[2]);

async function loadVariable() {
    const response = await fetch(`/api/variables/${variableId}`);
    const variable = await response.json();
    
    document.getElementById('name').value = variable.name;
    document.getElementById('value').value = variable.value;
    document.getElementById('description').value = variable.description || '';
    document.getElementById('is_secret').checked = variable.is_secret;
    
    // Set value_type radio button
    if (variable.value_type === 'number') {
        document.getElementById('type-number').checked = true;
    } else {
        document.getElementById('type-string').checked = true;
    }
}

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
        const response = await fetch(`/api/variables/${variableId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = '/variables';
        } else {
            const error = await response.json();
            alert(t('variable_update_failed') + ': ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        alert(t('variable_update_failed') + ': ' + error.message);
    }
});

// 言語初期化完了後にVariable情報を読み込む
(async () => {
    await initLanguageSwitcher();
    loadVariable();
})();
