/**
 * Variable新規登録画面
 */

function toggleSourceType() {
    const sourceType = document.querySelector('input[name="source_type"]:checked').value;
    const valueGroup = document.getElementById('value-input-group');
    const envGroup = document.getElementById('env-input-group');
    const valueInput = document.getElementById('value');
    const envInput = document.getElementById('env_var_name');
    const resultDiv = document.getElementById('env-check-result');
    
    if (sourceType === 'env') {
        valueGroup.style.display = 'none';
        envGroup.style.display = 'block';
        valueInput.removeAttribute('required');
        envInput.setAttribute('required', 'required');
    } else {
        valueGroup.style.display = 'block';
        envGroup.style.display = 'none';
        valueInput.setAttribute('required', 'required');
        envInput.removeAttribute('required');
    }
    
    // 結果表示をクリア
    if (resultDiv) {
        resultDiv.style.display = 'none';
    }
}

async function checkEnvVariable() {
    const envVarName = document.getElementById('env_var_name').value.trim();
    const resultDiv = document.getElementById('env-check-result');
    
    if (!envVarName) {
        resultDiv.style.display = 'block';
        resultDiv.style.backgroundColor = '#fee';
        resultDiv.style.border = '1px solid #fcc';
        resultDiv.style.color = '#c33';
        resultDiv.textContent = t('variable_env_name_required') || '環境変数名を入力してください';
        return;
    }
    
    try {
        const response = await fetch('/api/variables/check-env', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ env_var_name: envVarName })
        });
        
        const result = await response.json();
        
        resultDiv.style.display = 'block';
        if (result.exists) {
            resultDiv.style.backgroundColor = '#d1fae5';
            resultDiv.style.border = '1px solid #10b981';
            resultDiv.style.color = '#065f46';
            resultDiv.textContent = '✓ ' + (t('variable_env_value_found') || '値が取得できました');
        } else {
            resultDiv.style.backgroundColor = '#fee';
            resultDiv.style.border = '1px solid #fcc';
            resultDiv.style.color = '#c33';
            resultDiv.textContent = '✗ ' + (t('variable_env_value_not_found') || '環境変数が見つかりません');
        }
    } catch (error) {
        resultDiv.style.display = 'block';
        resultDiv.style.backgroundColor = '#fee';
        resultDiv.style.border = '1px solid #fcc';
        resultDiv.style.color = '#c33';
        resultDiv.textContent = '✗ ' + (t('error_unknown') || 'エラーが発生しました');
    }
}

document.getElementById('variable-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const sourceType = document.querySelector('input[name="source_type"]:checked').value;
    
    const data = {
        name: document.getElementById('name').value.toUpperCase(),
        value_type: document.querySelector('input[name="value_type"]:checked').value,
        source_type: sourceType,
        description: document.getElementById('description').value,
        is_secret: document.getElementById('is_secret').checked
    };
    
    if (sourceType === 'env') {
        data.env_var_name = document.getElementById('env_var_name').value;
        data.value = '';  // 環境変数の場合は値を空にする
    } else {
        data.value = document.getElementById('value').value;
    }
    
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
            await modal.error(t('variable_register_failed') + ': ' + (error.error || t('error_unknown')));
        }
    } catch (error) {
        await modal.error(t('variable_register_failed') + ': ' + error.message);
    }
});

// 言語初期化
(async () => {
    await initLanguageSwitcher();
})();
