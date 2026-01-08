/**
 * Variables一覧画面
 */

function toggleAccordion() {
    const content = document.getElementById('usage-accordion');
    const icon = document.querySelector('.accordion-icon');
    
    if (content.classList.contains('open')) {
        content.classList.remove('open');
        icon.classList.remove('rotate');
    } else {
        content.classList.add('open');
        icon.classList.add('rotate');
    }
}

async function loadVariables() {
    const response = await fetch('/api/variables');
    const variables = await response.json();
    
    const container = document.getElementById('variables-list');
    
    if (variables.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('variable_empty')}</div>`;
        return;
    }
    
    container.innerHTML = variables.map(variable => `
        <div class="list-item">
            <div class="list-item-main">
                <h3>${variable.name}</h3>
                <div class="list-item-meta">
                    ${variable.is_secret ? '<span class="badge badge-secret">🔒 Secret</span>' : '<span class="badge">Public</span>'}
                    <span class="badge badge-type">${variable.value_type === 'number' ? '🔢 Number' : '📝 String'}</span>
                    <span class="text-muted">${variable.source_type === 'env' ? t('variable_env_var_name_display') : t('variable_value_label')}: <code>${variable.value}</code></span>
                </div>
                ${variable.description ? `<p class="text-muted">${variable.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <a href="/variables/${variable.id}/edit" class="btn btn-sm btn-secondary">${t('button_edit')}</a>
                <button onclick="deleteVariable(${variable.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>
            </div>
        </div>
    `).join('');
}

async function deleteVariable(id) {
    if (!confirm(t('variable_delete_confirm'))) return;
    
    await fetch(`/api/variables/${id}`, { method: 'DELETE' });
    loadVariables();
}

// 言語初期化完了後にVariables一覧を読み込む
(async () => {
    await initLanguageSwitcher();
    loadVariables();
})();
