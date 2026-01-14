// templates/new.js - New Template Page

function addHeader() {
    const container = document.getElementById('headers-container');
    const row = document.createElement('div');
    row.className = 'header-row';
    row.innerHTML = `
        <input type="text" placeholder="Header Name (例: Authorization)" class="header-key">
        <input type="text" placeholder="Header Value (例: Bearer {token})" class="header-value">
        <button type="button" onclick="this.parentElement.remove()">削除</button>
    `;
    container.appendChild(row);
}

function getHeaders() {
    const headers = {};
    const rows = document.querySelectorAll('.header-row');
    rows.forEach(row => {
        const key = row.querySelector('.header-key').value.trim();
        const value = row.querySelector('.header-value').value.trim();
        if (key && value) {
            headers[key] = value;
        }
    });
    return headers;
}

document.getElementById('template-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value.trim(),
        icon: document.getElementById('icon').value.trim() || '📦',
        category: document.getElementById('category').value.trim() || 'General',
        description: document.getElementById('description').value.trim(),
        service_type: document.getElementById('service_type').value,
        common_headers: getHeaders()
    };
    
    try {
        const response = await fetch('/api/mcp-templates', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const template = await response.json();
            window.location.href = `/mcp-templates?message=${encodeURIComponent('登録しました')}`;
        } else {
            const error = await response.json();
            await modal.error('登録に失敗しました: ' + (error.error || t('error_unknown')));
        }
    } catch (e) {
        await modal.error('登録に失敗しました: ' + e.message);
    }
});

// Initialize
(async () => {
    await initLanguageSwitcher();
    // Add one header row by default
    addHeader();
})();
