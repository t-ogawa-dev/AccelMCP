// templates/list.js - Template List Page
let currentTab = 'api';
let selectedTemplateId = null;
let selectedMcpServiceId = null;
let createdAppId = null;

function showFlashMessage(message) {
    const flashDiv = document.getElementById('flash-message');
    flashDiv.textContent = message;
    flashDiv.style.display = 'block';
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        flashDiv.style.display = 'none';
    }, 5000);
}

async function loadTemplates(type) {
    let apiType = type;
    let containerId;
    
    if (type === 'api' || type === 'mcp') {
        apiType = 'builtin';
        containerId = `${type}-templates`;
    } else {
        containerId = 'custom-templates';
    }
    
    const response = await fetch(`/api/mcp-templates?type=${apiType}`);
    let templates = await response.json();
    
    // Filter by service_type for builtin templates
    if (type === 'api') {
        templates = templates.filter(t => t.service_type === 'api');
    } else if (type === 'mcp') {
        templates = templates.filter(t => t.service_type === 'mcp');
    }
    
    const container = document.getElementById(containerId);
    
    if (templates.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <p data-i18n="mcp_template_empty">${t('mcp_template_empty')}</p>
            </div>
        `;
        return;
    }
    
    // For API templates, fetch capability counts
    const capabilityCounts = {};
    if (type === 'api') {
        for (const template of templates) {
            try {
                const capResponse = await fetch(`/api/mcp-templates/${template.id}/capabilities`);
                if (capResponse.ok) {
                    const capabilities = await capResponse.json();
                    capabilityCounts[template.id] = capabilities.length;
                }
            } catch (e) {
                console.error(`Failed to load capabilities for template ${template.id}:`, e);
            }
        }
    }
    
    container.innerHTML = templates.map(template => {
        const officialLink = template.official_url ? 
            `<a href="${template.official_url}" target="_blank" class="template-link" onclick="event.stopPropagation()" title="公式サイト">🔗</a>` : '';
        
        const capabilityBadge = type === 'api' && capabilityCounts[template.id] ? 
            `<span class="capability-badge">${capabilityCounts[template.id]} APIs</span>` : '';
        
        return `
            <div class="template-card" onclick="window.location.href='/mcp-templates/${template.id}'">
                <div class="template-header">
                    <div class="template-icon">${template.icon || '📦'}</div>
                    <div class="template-info">
                        <div class="template-name">${template.name} ${officialLink}</div>
                        <div class="template-category">${template.category || 'General'} ${capabilityBadge}</div>
                    </div>
                </div>
                <div class="template-description">${template.description || ''}</div>
                ${template.mcp_url ? `<div class="template-url">${template.mcp_url}</div>` : ''}
                <div class="template-meta">
                    <div class="template-actions">
                        <button class="btn-small btn-use" onclick="useTemplate(${template.id}, event)" data-i18n="mcp_template_use_button">${t('mcp_template_use_button')}</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function useTemplate(templateId, event) {
    event.stopPropagation();
    selectedTemplateId = templateId;
    
    // Load MCP services
    loadMcpServicesForModal();
    
    // Show modal
    const modal = document.getElementById('use-template-modal');
    const errorDiv = document.getElementById('modal-error');
    
    modal.style.display = 'block';
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
}

async function loadMcpServicesForModal() {
    const select = document.getElementById('modal-mcp-service');
    
    try {
        const response = await fetch('/api/mcp-services');
        const services = await response.json();
        
        if (services.length === 0) {
            select.innerHTML = '<option value="" disabled>' + t('mcp_template_no_services') + '</option>';
            return;
        }
        
        select.innerHTML = services
            .filter(service => service.is_enabled)
            .map(service => 
                `<option value="${service.id}">${service.name} (${service.identifier})</option>`
            ).join('');
    } catch (e) {
        select.innerHTML = '<option value="" disabled>Failed to load services</option>';
    }
}

function closeModal() {
    const modal = document.getElementById('use-template-modal');
    const errorDiv = document.getElementById('modal-error');
    modal.style.display = 'none';
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
    selectedTemplateId = null;
}

function showModalError(message) {
    const errorDiv = document.getElementById('modal-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function showSuccessModal(serviceName) {
    const modal = document.getElementById('success-modal');
    const message = document.getElementById('success-message');
    message.textContent = serviceName;
    modal.style.display = 'block';
}

function closeSuccessModal() {
    const modal = document.getElementById('success-modal');
    modal.style.display = 'none';
}

function goToAppDetail() {
    if (selectedMcpServiceId && createdAppId) {
        window.location.href = `/mcp-services/${selectedMcpServiceId}/apps/${createdAppId}`;
    } else if (selectedMcpServiceId) {
        window.location.href = `/mcp-services/${selectedMcpServiceId}/apps`;
    } else {
        window.location.href = '/mcp-services';
    }
}

function confirmTemplateUse() {
    const select = document.getElementById('modal-mcp-service');
    const mcpServiceId = select.value;
    
    if (!mcpServiceId) {
        showModalError(t('mcp_template_select_service_required'));
        return;
    }
    
    // Save IDs before applying
    const templateId = selectedTemplateId;
    selectedMcpServiceId = mcpServiceId;
    applyTemplate(templateId, mcpServiceId);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const useModal = document.getElementById('use-template-modal');
    const successModal = document.getElementById('success-modal');
    if (event.target === useModal) {
        closeModal();
    }
    // Success modal should not close on outside click
}

// Handle Enter key in modal
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('modal-subdomain');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                confirmTemplateUse();
            }
        });
    }
});


async function applyTemplate(templateId, mcpServiceId) {
    try {
        const response = await fetch(`/api/mcp-templates/${templateId}/prepare-app`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({mcp_service_id: mcpServiceId})
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Store template data in sessionStorage for the form to use
            sessionStorage.setItem('app_template_data', JSON.stringify(result.template_data));
            
            // Redirect to app creation form with template flag
            window.location.href = result.redirect_url + '?from=template';
        } else {
            // Handle non-OK response
            let errorMessage = 'Unknown error';
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                const error = await response.json();
                errorMessage = error.error || error.message || errorMessage;
            } else {
                errorMessage = `Server error (${response.status})`;
            }
            
            showModalError(t('app_register_failed') + ': ' + errorMessage);
        }
    } catch (e) {
        console.error('Apply template exception:', e);
        showModalError(t('app_register_failed') + ': ' + e.message);
    }
}

async function exportTemplate(templateId, event) {
    event.stopPropagation();
    
    try {
        const response = await fetch(`/api/mcp-templates/${templateId}/export`);
        const data = await response.json();
        
        // Download as JSON file
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export-template-${data.name}.json`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (e) {
        alert('Export failed: ' + e.message);
    }
}

function editTemplate(templateId, event) {
    event.stopPropagation();
    window.location.href = `/mcp-templates/${templateId}/edit`;
}

function viewCapabilities(templateId, event) {
    event.stopPropagation();
    window.location.href = `/mcp-templates/${templateId}/capabilities`;
}

async function deleteTemplate(templateId, event) {
    event.stopPropagation();
    
    if (!confirm(t('mcp_template_delete_confirm'))) return;
    
    try {
        const response = await fetch(`/api/mcp-templates/${templateId}`, {method: 'DELETE'});
        if (response.ok) {
            showFlashMessage('削除しました');
            loadTemplates('custom');
        } else {
            const error = await response.json();
            alert(error.error || 'Delete failed');
        }
    } catch (e) {
        alert('Delete failed: ' + e.message);
    }
}

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        // Update active tab
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Show/hide content
        document.getElementById('api-tab').style.display = tabName === 'api' ? 'block' : 'none';
        document.getElementById('mcp-tab').style.display = tabName === 'mcp' ? 'block' : 'none';
        document.getElementById('custom-tab').style.display = tabName === 'custom' ? 'block' : 'none';
        
        currentTab = tabName;
        loadTemplates(tabName);
    });
});

// Import functionality
let selectedFile = null;

function openImportModal() {
    const modal = document.getElementById('import-modal');
    const errorDiv = document.getElementById('import-error');
    modal.style.display = 'block';
    errorDiv.style.display = 'none';
    clearFile();
}

function closeImportModal() {
    const modal = document.getElementById('import-modal');
    modal.style.display = 'none';
    clearFile();
}

function clearFile() {
    selectedFile = null;
    document.getElementById('file-input').value = '';
    const dropZoneContent = document.querySelector('.drop-zone-content');
    const fileInfo = document.getElementById('file-info');
    if (dropZoneContent) dropZoneContent.style.display = 'flex';
    if (fileInfo) fileInfo.style.display = 'none';
    document.getElementById('import-btn').disabled = true;
}

function showImportError(message) {
    const errorDiv = document.getElementById('import-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function handleFileSelect(file) {
    if (!file) return;
    
    if (!file.name.endsWith('.json')) {
        showImportError('JSONファイルを選択してください');
        return;
    }
    
    selectedFile = file;
    document.getElementById('drop-zone').querySelector('.drop-zone-content').style.display = 'none';
    const fileInfo = document.getElementById('file-info');
    fileInfo.style.display = 'flex';
    fileInfo.querySelector('.file-info-name').textContent = file.name;
    document.getElementById('import-btn').disabled = false;
    document.getElementById('import-error').style.display = 'none';
}

async function confirmImport() {
    if (!selectedFile) return;
    
    try {
        const text = await selectedFile.text();
        const data = JSON.parse(text);
        
        const response = await fetch('/api/mcp-templates/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            closeImportModal();
            // Reload page with success message
            window.location.href = '/mcp-templates?message=' + encodeURIComponent('インポートしました！');
        } else {
            const error = await response.json();
            showImportError(error.error || 'インポートに失敗しました');
        }
    } catch (e) {
        showImportError('ファイルの読み込みに失敗しました: ' + e.message);
    }
}

// Setup drag and drop
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    
    if (!dropZone || !fileInput) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });
    
    // Highlight drop zone when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
});

// Initialize
(async () => {
    await initLanguageSwitcher();
    
    // Check for template updates on page load
    checkTemplateUpdatesOnLoad();
    
    // Check for flash message in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    if (message) {
        showFlashMessage(decodeURIComponent(message));
        // Remove message from URL
        window.history.replaceState({}, '', '/mcp-templates');
        
        // Switch to custom tab when showing flash message
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelector('.tab[data-tab="custom"]').classList.add('active');
        document.getElementById('api-tab').style.display = 'none';
        document.getElementById('mcp-tab').style.display = 'none';
        document.getElementById('custom-tab').style.display = 'block';
        currentTab = 'custom';
        loadTemplates('custom');
    } else {
        loadTemplates('api');
    }
})();

// ============= Template Update Functions =============

async function checkTemplateUpdatesOnLoad() {
    try {
        const response = await fetch('/api/templates/check-updates');
        if (response.ok) {
            const data = await response.json();
            if (data.has_update) {
                document.getElementById('update-badge').style.display = 'inline-block';
            }
        }
    } catch (error) {
        console.error('Failed to check for template updates:', error);
    }
}

async function checkTemplateUpdates() {
    const updateModal = document.getElementById('update-modal');
    const updateError = document.getElementById('update-error');
    const updateCheckContent = document.getElementById('update-check-content');
    const updateProgress = document.getElementById('update-progress');
    const syncBtn = document.getElementById('sync-btn');
    
    updateModal.style.display = 'block';
    updateCheckContent.style.display = 'none';
    updateProgress.style.display = 'block';
    updateError.style.display = 'none';
    syncBtn.style.display = 'none';
    
    try {
        const response = await fetch('/api/templates/check-updates');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to check for updates');
        }
        
        updateProgress.style.display = 'none';
        updateCheckContent.style.display = 'block';
        
        if (data.has_update) {
            document.getElementById('update-modal-title').textContent = t('mcp_template_update_available') || '最新版のテンプレートがあります';
            document.getElementById('update-modal-message').textContent = 
                t('mcp_template_update_confirm') || 'テンプレートを最新版に同期しますか？';
            document.getElementById('current-version').textContent = data.current_version;
            document.getElementById('latest-version').textContent = data.latest_version;
            document.getElementById('changelog').textContent = data.changelog;
            syncBtn.style.display = 'inline-block';
        } else {
            document.getElementById('update-modal-title').textContent = t('mcp_template_up_to_date') || '最新の状態です';
            document.getElementById('update-modal-message').textContent = 
                t('mcp_template_no_update') || 'テンプレートは最新版です。';
            document.getElementById('current-version').textContent = data.current_version;
            document.getElementById('latest-version').textContent = data.latest_version;
            document.getElementById('changelog').textContent = '-';
            document.getElementById('update-details').style.display = 'none';
        }
    } catch (error) {
        updateProgress.style.display = 'none';
        updateCheckContent.style.display = 'none';
        updateError.textContent = error.message;
        updateError.style.display = 'block';
    }
}

async function syncTemplates() {
    const updateCheckContent = document.getElementById('update-check-content');
    const updateProgress = document.getElementById('update-progress');
    const updateError = document.getElementById('update-error');
    const syncBtn = document.getElementById('sync-btn');
    
    updateCheckContent.style.display = 'none';
    updateProgress.style.display = 'block';
    updateError.style.display = 'none';
    syncBtn.disabled = true;
    
    try {
        const response = await fetch('/api/templates/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to sync templates');
        }
        
        // Success - close modal and reload templates
        closeUpdateModal();
        showFlashMessage(
            `${t('mcp_template_sync_success') || 'テンプレートを同期しました'}: ${data.added} ${t('added') || '追加'}, ${data.updated} ${t('updated') || '更新'}`
        );
        
        // Hide update badge
        document.getElementById('update-badge').style.display = 'none';
        
        // Reload templates
        loadTemplates(currentTab);
        
    } catch (error) {
        updateProgress.style.display = 'none';
        updateCheckContent.style.display = 'block';
        updateError.textContent = error.message;
        updateError.style.display = 'block';
        syncBtn.disabled = false;
    }
}

function closeUpdateModal() {
    document.getElementById('update-modal').style.display = 'none';
    document.getElementById('update-details').style.display = 'block';
    document.getElementById('sync-btn').disabled = false;
}
