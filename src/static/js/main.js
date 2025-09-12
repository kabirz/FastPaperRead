// Main JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    console.log('ReadPaper With Code - Main JS Loaded');
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Utility Functions
const Utils = {
    // Show loading state
    showLoading: function(element) {
        if (element) {
            element.disabled = true;
            element.classList.add('processing');
            const originalText = element.textContent;
            element.dataset.originalText = originalText;
            element.innerHTML = '<span class="loading"></span> 处理中...';
        }
    },
    
    // Hide loading state
    hideLoading: function(element) {
        if (element) {
            element.disabled = false;
            element.classList.remove('processing');
            element.textContent = element.dataset.originalText || '开始分析';
        }
    },
    
    // Show error message
    showError: function(message, container = null) {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <strong>错误：</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        if (container) {
            container.innerHTML = alertHtml;
            container.style.display = 'block';
        } else {
            // Default error container
            const errorAlert = document.getElementById('errorAlert');
            if (errorAlert) {
                document.getElementById('errorMessage').textContent = message;
                errorAlert.style.display = 'block';
            }
        }
    },
    
    // Hide error message
    hideError: function(container = null) {
        if (container) {
            container.style.display = 'none';
        } else {
            const errorAlert = document.getElementById('errorAlert');
            if (errorAlert) {
                errorAlert.style.display = 'none';
            }
        }
    },
    
    // Update progress
    updateProgress: function(percentage, text) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
        }
        
        if (progressText) {
            progressText.textContent = text;
        }
    },
    
    // Show progress card
    showProgress: function() {
        const progressCard = document.getElementById('progressCard');
        if (progressCard) {
            progressCard.style.display = 'block';
            progressCard.classList.add('fade-in');
        }
    },
    
    // Hide progress card
    hideProgress: function() {
        const progressCard = document.getElementById('progressCard');
        if (progressCard) {
            progressCard.style.display = 'none';
        }
    },
    
    // Validate URL
    isValidUrl: function(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    },
    
    // Validate PDF URL
    isValidPdfUrl: function(url) {
        if (!this.isValidUrl(url)) return false;
        
        const pdfPatterns = [
            /\.pdf$/i,
            /arxiv\.org\/pdf/i,
            /ieee/i,
            /acm/i
        ];
        
        return pdfPatterns.some(pattern => pattern.test(url));
    },
    
    // Debounce function
    debounce: function(func, wait, immediate) {
        var timeout;
        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }
};

// API Helper
const API = {
    baseUrl: '',
    
    // Make API request
    request: async function(endpoint, options = {}) {
        const url = this.baseUrl + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const config = Object.assign({}, defaultOptions, options);
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // Process paper
    processPaper: async function(data) {
        return this.request('/process', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};

// Make utilities globally available
window.Utils = Utils;
window.API = API;