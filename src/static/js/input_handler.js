// Input Form Handler

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('paperForm');
    const submitBtn = document.getElementById('submitBtn');
    const addKnowledgeBtn = document.getElementById('addKnowledgeUrl');
    const knowledgeUrlsContainer = document.getElementById('knowledgeUrls');
    
    // Form submission
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // Add knowledge URL
    if (addKnowledgeBtn) {
        addKnowledgeBtn.addEventListener('click', addKnowledgeUrlField);
    }
    
    // Remove knowledge URL handlers
    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-url')) {
            removeKnowledgeUrlField(e.target.closest('.input-group'));
        }
    });
    
    // Real-time validation
    const pdfUrlInput = document.getElementById('pdfUrl');
    if (pdfUrlInput) {
        pdfUrlInput.addEventListener('input', Utils.debounce(validatePdfUrl, 300));
    }
});

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = document.getElementById('submitBtn');
    
    // Validate form
    if (!validateForm()) {
        return;
    }
    
    // Prepare data
    const data = {
        pdf_url: formData.get('pdf_url'),
        git_url: formData.get('git_url') || null,
        knowledge_urls: Array.from(formData.getAll('knowledge_urls[]')).filter(url => url.trim())
    };
    
    try {
        // Show loading state
        Utils.showLoading(submitBtn);
        Utils.hideError();
        Utils.showProgress();
        Utils.updateProgress(10, '开始处理...');
        
        // Step 1: Download and process PDF
        Utils.updateProgress(25, '下载和处理PDF文件...');
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
        
        // Step 2: Analyze code (if applicable)
        Utils.updateProgress(50, '分析代码仓库...');
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Step 3: Process with AI
        Utils.updateProgress(75, '使用AI分析论文内容...');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Step 4: Generate blog
        Utils.updateProgress(90, '生成Blog内容...');
        
        // Make API request
        const result = await API.processPaper(data);
        
        if (result.success) {
            Utils.updateProgress(100, '完成！');
            
            // Display results
            setTimeout(() => {
                displayResults(result.blog_html);
            }, 500);
        } else {
            throw new Error(result.error || '处理失败');
        }
        
    } catch (error) {
        console.error('Processing error:', error);
        Utils.showError(error.message || '处理过程中发生错误，请稍后重试。');
        Utils.hideProgress();
    } finally {
        Utils.hideLoading(submitBtn);
    }
}

// Validate form
function validateForm() {
    const pdfUrl = document.getElementById('pdfUrl').value.trim();
    
    if (!pdfUrl) {
        Utils.showError('请输入PDF链接');
        return false;
    }
    
    if (!Utils.isValidUrl(pdfUrl)) {
        Utils.showError('请输入有效的PDF链接');
        return false;
    }
    
    // Validate knowledge URLs
    const knowledgeUrls = document.querySelectorAll('.knowledge-url');
    for (let input of knowledgeUrls) {
        const url = input.value.trim();
        if (url && !Utils.isValidUrl(url)) {
            Utils.showError(`知识库链接格式不正确: ${url}`);
            return false;
        }
    }
    
    return true;
}

// Validate PDF URL
function validatePdfUrl() {
    const input = document.getElementById('pdfUrl');
    const url = input.value.trim();
    
    if (url) {
        if (Utils.isValidUrl(url)) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    } else {
        input.classList.remove('is-valid', 'is-invalid');
    }
}

// Add knowledge URL field
function addKnowledgeUrlField() {
    const container = document.getElementById('knowledgeUrls');
    const newField = document.createElement('div');
    newField.className = 'input-group mb-2 fade-in';
    newField.innerHTML = `
        <input 
            type="url" 
            class="form-control knowledge-url" 
            name="knowledge_urls[]"
            placeholder="https://example.com/knowledge-base"
        >
        <button class="btn btn-outline-danger remove-url" type="button">
            <i class="fas fa-minus"></i>
        </button>
    `;
    
    container.appendChild(newField);
}

// Remove knowledge URL field
function removeKnowledgeUrlField(fieldGroup) {
    const container = document.getElementById('knowledgeUrls');
    if (container.children.length > 1) {
        fieldGroup.remove();
    }
}

// Display results
function displayResults(blogHtml) {
    if (blogHtml) {
        // Create new window/tab for results
        const newWindow = window.open('', '_blank');
        newWindow.document.write(blogHtml);
        newWindow.document.close();
    } else {
        Utils.showError('未能生成分析结果');
    }
}

// Auto-save form data (optional feature)
function saveFormData() {
    const formData = {
        pdf_url: document.getElementById('pdfUrl').value,
        git_url: document.getElementById('gitUrl').value,
        knowledge_urls: Array.from(document.querySelectorAll('.knowledge-url')).map(input => input.value)
    };
    
    localStorage.setItem('paperFormData', JSON.stringify(formData));
}

// Restore form data (optional feature)
function restoreFormData() {
    const savedData = localStorage.getItem('paperFormData');
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            
            if (data.pdf_url) {
                document.getElementById('pdfUrl').value = data.pdf_url;
            }
            
            if (data.git_url) {
                document.getElementById('gitUrl').value = data.git_url;
            }
            
            if (data.knowledge_urls && data.knowledge_urls.length > 0) {
                // Clear existing fields
                const container = document.getElementById('knowledgeUrls');
                container.innerHTML = '';
                
                // Add saved URLs
                data.knowledge_urls.forEach((url, index) => {
                    if (index === 0) {
                        // First field
                        container.innerHTML = `
                            <div class="input-group mb-2">
                                <input 
                                    type="url" 
                                    class="form-control knowledge-url" 
                                    name="knowledge_urls[]"
                                    value="${url}"
                                    placeholder="https://example.com/knowledge-base"
                                >
                                <button class="btn btn-outline-danger remove-url" type="button">
                                    <i class="fas fa-minus"></i>
                                </button>
                            </div>
                        `;
                    } else if (url.trim()) {
                        // Additional fields
                        addKnowledgeUrlField();
                        const inputs = container.querySelectorAll('.knowledge-url');
                        inputs[inputs.length - 1].value = url;
                    }
                });
            }
        } catch (error) {
            console.error('Error restoring form data:', error);
        }
    }
}

// Initialize form restoration
document.addEventListener('DOMContentLoaded', function() {
    // Uncomment to enable auto-restore
    // restoreFormData();
    
    // Auto-save on input change (debounced)
    const form = document.getElementById('paperForm');
    if (form) {
        form.addEventListener('input', Utils.debounce(saveFormData, 1000));
    }
});