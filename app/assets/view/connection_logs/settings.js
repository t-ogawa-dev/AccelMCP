/**
 * Connection Log Settings Page
 * Manage logging configuration
 */

document.addEventListener('DOMContentLoaded', async () => {
    await initLanguageSwitcher();
    await loadSettings();
    setupEventListeners();
});

let currentSettings = {};

async function loadSettings() {
    try {
        const response = await fetch('/api/admin/log-settings');
        if (!response.ok) throw new Error('Failed to load settings');
        
        currentSettings = await response.json();
        populateForm(currentSettings);
        
    } catch (error) {
        console.error('Failed to load settings:', error);
        showToast(t('error_loading_settings'), 'error');
    }
}

function populateForm(settings) {
    // Enabled switch
    document.getElementById('mcp_log_enabled').checked = settings.enabled;
    
    // Max body size
    document.getElementById('mcp_log_max_body_size').value = settings.max_body_size || 10000;
    
    // Masking presets
    document.getElementById('mcp_log_mask_credit_card').checked = settings.mask_credit_card;
    document.getElementById('mcp_log_mask_email').checked = settings.mask_email;
    document.getElementById('mcp_log_mask_phone').checked = settings.mask_phone;
    
    // Custom patterns
    document.getElementById('mcp_log_mask_custom_patterns').value = settings.custom_patterns || '';
}

function setupEventListeners() {
    // Form submit
    const form = document.getElementById('settings-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        saveSettings();
    });
    
    // Cleanup button
    document.getElementById('cleanup-btn').addEventListener('click', executeCleanup);
}

async function saveSettings() {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = t('saving');
    
    try {
        const settings = {
            enabled: document.getElementById('mcp_log_enabled').checked,
            max_body_size: parseInt(document.getElementById('mcp_log_max_body_size').value, 10),
            mask_credit_card: document.getElementById('mcp_log_mask_credit_card').checked,
            mask_email: document.getElementById('mcp_log_mask_email').checked,
            mask_phone: document.getElementById('mcp_log_mask_phone').checked,
            custom_patterns: document.getElementById('mcp_log_mask_custom_patterns').value
        };
        
        // Validate
        if (settings.max_body_size < 1024 || settings.max_body_size > 102400) {
            showToast(t('error_max_body_size'), 'error');
            return;
        }
        
        // Validate custom patterns
        if (settings.custom_patterns) {
            const patterns = settings.custom_patterns.split('\n').filter(p => p.trim());
            for (const pattern of patterns) {
                try {
                    new RegExp(pattern.trim());
                } catch (e) {
                    showToast(`${t('error_invalid_pattern')}: ${pattern}`, 'error');
                    return;
                }
            }
        }
        
        const response = await fetch('/api/admin/log-settings', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        if (!response.ok) throw new Error('Failed to save settings');
        
        currentSettings = settings;
        showToast(t('settings_saved'), 'success');
        
    } catch (error) {
        console.error('Failed to save settings:', error);
        showToast(t('error_saving_settings'), 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

async function executeCleanup() {
    const days = parseInt(document.getElementById('cleanup-days').value, 10);
    
    if (!days || days < 1) {
        showToast(t('error_cleanup_days'), 'error');
        return;
    }
    
    if (!confirm(t('cleanup_confirm'))) {
        return;
    }
    
    const cleanupBtn = document.getElementById('cleanup-btn');
    const originalText = cleanupBtn.innerHTML;
    cleanupBtn.disabled = true;
    cleanupBtn.textContent = t('cleaning_up');
    
    const resultDiv = document.getElementById('cleanup-result');
    
    try {
        const response = await fetch(`/api/connection-logs/cleanup?days=${days}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to cleanup logs');
        
        const result = await response.json();
        
        resultDiv.className = 'cleanup-result success';
        resultDiv.textContent = `${result.deleted_count}${t('cleanup_success')}`;
        resultDiv.style.display = 'block';
        
    } catch (error) {
        console.error('Failed to cleanup logs:', error);
        resultDiv.className = 'cleanup-result error';
        resultDiv.textContent = t('error_cleanup');
        resultDiv.style.display = 'block';
    } finally {
        cleanupBtn.disabled = false;
        cleanupBtn.innerHTML = originalText;
    }
}

function showToast(message, type = 'info') {
    // Remove existing toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    if (type === 'success') {
        toast.style.backgroundColor = '#4CAF50';
    } else if (type === 'error') {
        toast.style.backgroundColor = '#f44336';
    } else {
        toast.style.backgroundColor = '#2196F3';
    }
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
