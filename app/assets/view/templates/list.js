// templates/list.js - Template List Page
let currentTab = 'api';
let selectedTemplateId = null;

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
    
    // Fetch full template details with capabilities for each template
    const templatesWithDetails = await Promise.all(
        templates.map(async (template) => {
            try {
                const detailResponse = await fetch(`/api/mcp-templates/${template.id}`);
                const detail = await detailResponse.json();
                return { ...template, capabilities: detail.capabilities || [] };
            } catch (e) {
                return { ...template, capabilities: [] };
            }
        })
    );
    
    container.innerHTML = templatesWithDetails.map(template => `
        <div class="template-card" onclick="window.location.href='/mcp-templates/${template.id}'">
            <div class="template-header">
                <div class="template-icon">${template.icon || '📦'}</div>
                <div class="template-info">
                    <div class="template-name">${template.name}</div>
                    <div class="template-category">${template.category || 'General'}</div>
                </div>
            </div>
            <div class="template-description">${template.description || ''}</div>
            <div class="template-meta">
                <div class="template-capabilities">
                    <span data-i18n="mcp_template_capabilities_count">${t('mcp_template_capabilities_count')}</span>: ${template.capabilities.length}
                </div>
                <div class="template-actions">
                    <button class="btn-small btn-use" onclick="useTemplate(${template.id}, event)" data-i18n="mcp_template_use_button">${t('mcp_template_use_button')}</button>
                </div>
            </div>
        </div>
    `).join('');
}

function useTemplate(templateId, event) {
    event.stopPropagation();
    selectedTemplateId = templateId;
    
    // Show modal
    const modal = document.getElementById('use-template-modal');
    const input = document.getElementById('modal-subdomain');
    const errorDiv = document.getElementById('modal-error');
    
    modal.style.display = 'block';
    input.value = '';
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
    input.focus();
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

function goToServiceList() {
    window.location.href = '/apps';
}

function confirmTemplateUse() {
    const subdomain = document.getElementById('modal-subdomain').value.trim();
    
    if (!subdomain) {
        showModalError(t('app_subdomain_input') + ' is required');
        return;
    }
    
    // Validate subdomain format
    const pattern = /^[a-z0-9-]+$/;
    if (!pattern.test(subdomain)) {
        showModalError(t('app_subdomain_hint'));
        return;
    }
    
    // Save templateId before closing modal
    const templateId = selectedTemplateId;
    applyTemplate(templateId, subdomain);
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


async function applyTemplate(templateId, subdomain) {
    try {
        const response = await fetch(`/api/mcp-templates/${templateId}/apply`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({subdomain})
        });
        
        if (response.ok) {
            const service = await response.json();
            closeModal();
            showSuccessModal(service.name);
        } else {
            // Handle non-OK response
            let errorMessage = 'Unknown error';
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                const error = await response.json();
                errorMessage = error.error || error.message || errorMessage;
            } else {
                // Server returned HTML (likely an error page)
                errorMessage = `Server error (${response.status})`;
            }
            
            if (response.status === 409) {
                showModalError('このサブドメインは既に使用されています。別のサブドメインを指定してください。');
            } else {
                showModalError(t('app_register_failed') + ': ' + errorMessage);
            }
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
