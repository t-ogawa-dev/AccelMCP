/**
 * MCPサービス一覧画面
 */

async function loadMcpServices() {
    const response = await fetch('/api/mcp-services');
    const services = await response.json();
    
    const container = document.getElementById('services-list');
    
    if (services.length === 0) {
        container.innerHTML = `<div class="empty-state">${t('mcp_service_empty')}</div>`;
        return;
    }
    
    container.innerHTML = services.map(service => `
        <div class="list-item ${!service.is_enabled ? 'disabled' : ''}">
            <div class="list-item-main">
                <h3><a href="/mcp-services/${service.id}">${service.name}</a></h3>
                <div class="list-item-meta">
                    <span class="badge">${t('mcp_service_subdomain')}: ${service.subdomain}</span>
                    ${!service.is_enabled ? `<span class="status-badge disabled">${t('status_disabled')}</span>` : `<span class="status-badge enabled">${t('status_enabled')}</span>`}
                    <span class="text-muted">${t('mcp_service_apps_count')}: ${service.apps_count || 0}</span>
                </div>
                ${service.description ? `<p class="text-muted">${service.description}</p>` : ''}
            </div>
            <div class="list-item-actions">
                <label class="toggle-switch">
                    <input type="checkbox" ${service.is_enabled ? 'checked' : ''} onchange="toggleMcpService(${service.id})">
                    <span class="toggle-slider"></span>
                </label>
                <a href="/mcp-services/${service.id}/apps" class="btn btn-sm">${t('mcp_service_apps_button')}</a>
                <a href="/mcp-services/${service.id}/edit" class="btn btn-sm">${t('button_edit')}</a>
                <button onclick="deleteMcpService(${service.id})" class="btn btn-sm btn-danger">${t('button_delete')}</button>
            </div>
        </div>
    `).join('');
}

async function toggleMcpService(id) {
    try {
        const response = await fetch(`/api/mcp-services/${id}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            loadMcpServices();
        } else {
            const error = await response.json();
            alert('切り替えに失敗しました: ' + (error.error || 'Unknown error'));
        }
    } catch (e) {
        alert('切り替えに失敗しました: ' + e.message);
    }
}

async function deleteMcpService(id) {
    if (!confirm(t('mcp_service_delete_confirm'))) return;
    
    await fetch(`/api/mcp-services/${id}`, { method: 'DELETE' });
    loadMcpServices();
}

// Import Modal Functions
let selectedFile = null;

function openImportModal() {
    document.getElementById('import-modal').style.display = 'block';
    document.getElementById('import-error').style.display = 'none';
    clearFile();
}

function closeImportModal() {
    document.getElementById('import-modal').style.display = 'none';
    clearFile();
}

function clearFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').style.display = 'none';
    document.querySelector('.drop-zone-content').style.display = 'flex';
    document.getElementById('import-btn').disabled = true;
}

function handleFileSelect(file) {
    if (!file || !file.name.endsWith('.json')) {
        showImportError(currentLanguage === 'ja' ? 'JSONファイルを選択してください' : 'Please select a JSON file');
        return;
    }
    
    selectedFile = file;
    document.getElementById('file-info-name').textContent = file.name;
    document.getElementById('file-info').style.display = 'flex';
    document.querySelector('.drop-zone-content').style.display = 'none';
    document.getElementById('import-btn').disabled = false;
    document.getElementById('import-error').style.display = 'none';
}

function showImportError(message) {
    const errorDiv = document.getElementById('import-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

async function confirmImport() {
    if (!selectedFile) return;
    
    try {
        const text = await selectedFile.text();
        const data = JSON.parse(text);
        
        const response = await fetch('/api/mcp-services/import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Import failed');
        }
        
        const result = await response.json();
        
        closeImportModal();
        
        // Show success message with subdomain change warning if applicable
        let message = currentLanguage === 'ja' ? 'インポートしました' : 'Imported successfully';
        if (result.subdomain_changed) {
            message += currentLanguage === 'ja' 
                ? `\n\nサブドメインが重複していたため、新しいサブドメイン「${result.mcp_service.subdomain}」が割り当てられました。`
                : `\n\nSubdomain was changed to "${result.mcp_service.subdomain}" due to conflict.`;
        }
        alert(message);
        
        loadMcpServices();
    } catch (error) {
        console.error('Import error:', error);
        showImportError(error.message || (currentLanguage === 'ja' ? 'インポートに失敗しました' : 'Import failed'));
    }
}

// Setup drag and drop
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    });
}

if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFileSelect(file);
    });
}

// 言語初期化完了後にMCPサービス一覧を読み込む
(async () => {
    await initLanguageSwitcher();
    loadMcpServices();
})();
