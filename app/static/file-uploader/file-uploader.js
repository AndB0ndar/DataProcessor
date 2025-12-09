class FileUploader {
    constructor(url_api_update) {
        this.url_api_update = url_api_update
        this.form = document.getElementById('uploadForm');
        this.fileInput = document.getElementById('fileInput');
        this.dropzone = document.querySelector('.file-uploader__dropzone');
        this.preview = document.getElementById('filePreview');
        this.feedback = document.getElementById('feedback');
        this.submitBtn = document.getElementById('submitBtn');
        this.dropzoneText = document.getElementById('dropzoneText');
        
        this.files = [];
        this.validExtensions = {
            config: ['json', 'yaml', 'yml', 'conf'],
            sources: ['v', 'vh', 'sv'] // Убрали архивы
        };
        
        this.maxFileSizes = {
            config: 10 * 1024 * 1024, // 10MB
            sources: 50 * 1024 * 1024 // 50MB
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        //this.dropzone.addEventListener('click', () => this.fileInput.click());
        this.dropzone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.dropzone.addEventListener('drop', (e) => this.handleDrop(e));
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
    
    handleFileSelect(event) {
        const newFiles = Array.from(event.target.files);
        this.processFiles(newFiles);
    }
    
    handleDragOver(event) {
        event.preventDefault();
        this.dropzone.classList.add('file-uploader__dropzone--dragover');
    }
    
    handleDrop(event) {
        event.preventDefault();
        this.dropzone.classList.remove('file-uploader__dropzone--dragover');
        
        const newFiles = Array.from(event.dataTransfer.files);
        this.processFiles(newFiles);
    }
    
    processFiles(newFiles) {
        const validFiles = newFiles.filter(file => this.validateFile(file));
        this.files = [...this.files, ...validFiles];
        
        this.updatePreview();
        this.updateUI();
    }
    
    validateFile(file) {
        const extension = this.getFileExtension(file.name);
        const fileType = this.getFileType(file.name);
        const allExtensions = [...this.validExtensions.config, ...this.validExtensions.sources];
        
        // Проверка расширения
        if (!allExtensions.includes(extension)) {
            this.showFeedback(
                `Неподдерживаемый формат: ${file.name}. ` +
                `Допустимые: ${allExtensions.join(', ')}`, 
                'error'
            );
            return false;
        }
        
        // Проверка размера
        const maxSize = fileType === 'config' ? this.maxFileSizes.config : this.maxFileSizes.sources;
        if (file.size > maxSize) {
            this.showFeedback(
                `Файл слишком большой: ${file.name} (${this.formatFileSize(file.size)}). ` +
                `Максимальный размер: ${this.formatFileSize(maxSize)}`, 
                'error'
            );
            return false;
        }
        
        return true;
    }
    
    getFileExtension(filename) {
        return filename.toLowerCase().split('.').pop();
    }
    
    getFileType(filename) {
        const extension = this.getFileExtension(filename);
        return this.validExtensions.config.includes(extension) ? 'config' : 'sources';
    }
    
    updatePreview() {
        this.preview.innerHTML = this.files.map((file, index) => this.createFilePreview(file, index)).join('');
        this.preview.classList.toggle('file-uploader__preview--visible', this.files.length > 0);
    }
    
    createFilePreview(file, index) {
        const type = this.getFileType(file.name);
        const typeClass = type === 'config' ? 'file-uploader__config' : 'file-uploader__sources';
        const typeLabel = type === 'config' ? 'Конфигурация' : 'Verilog';
        
        return `
            <div class="file-uploader__details ${typeClass}">
                <span class="file-uploader__filename">${file.name}</span>
                <button type="button" class="button button--ghost button--icon-only file-uploader__remove" 
                        data-index="${index}" aria-label="Удалить файл">
                    <span class="button__icon">✕</span>
                </button>
            </div>
            <div class="file-uploader__meta">
                ${this.formatFileSize(file.size)} • ${typeLabel}
            </div>
        `;
    }
    
    updateUI() {
        this.updateDropzoneText();
        this.updateSubmitButton();
        this.updateFeedback();
        this.bindRemoveEvents();
    }
    
    updateDropzoneText() {
        const fileCount = this.files.length;
        if (fileCount === 0) {
            this.dropzoneText.textContent = 'Перетащите файлы сюда или нажмите для выбора';
        } else {
            const configCount = this.files.filter(f => this.getFileType(f.name) === 'config').length;
            const sourcesCount = this.files.filter(f => this.getFileType(f.name) === 'sources').length;
            
            this.dropzoneText.textContent = 
                `Загружено: ${configCount} конфигурационных, ${sourcesCount} исходных файлов`;
        }
    }
    
    updateSubmitButton() {
        const hasConfig = this.files.some(file => this.getFileType(file.name) === 'config');
        const hasSources = this.files.some(file => this.getFileType(file.name) === 'sources');
        
        this.submitBtn.disabled = !(hasConfig && hasSources);
        this.submitBtn.classList.toggle('button--disabled', !(hasConfig && hasSources));
    }
    
    updateFeedback() {
        const configFiles = this.files.filter(f => this.getFileType(f.name) === 'config');
        const sourceFiles = this.files.filter(f => this.getFileType(f.name) === 'sources');
        
        if (configFiles.length > 0 && sourceFiles.length > 0) {
            if (configFiles.length === 1) {
                this.showFeedback('Все файлы загружены! Можно запускать обработку.', 'success');
            } else {
                this.showFeedback(
                    `Загружено ${configFiles.length} конфигурационных файлов. ` +
                    'Будет использован первый файл.', 
                    'warning'
                );
            }
        } else if (this.files.length > 0) {
            const missing = [];
            if (configFiles.length === 0) missing.push('конфигурационный файл');
            if (sourceFiles.length === 0) missing.push('исходные файлы Verilog');
            this.showFeedback(`Не хватает: ${missing.join(', ')}`, 'warning');
        } else {
            this.hideFeedback();
        }
    }
    
    bindRemoveEvents() {
        const removeButtons = this.preview.querySelectorAll('.file-uploader__remove');
        removeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const index = parseInt(e.target.closest('button').dataset.index);
                this.removeFile(index);
            });
        });
    }
    
    removeFile(index) {
        this.files.splice(index, 1);
        this.updatePreview();
        this.updateUI();
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        if (!this.validateSubmission()) {
            return;
        }
        
        try {
            await this.submitFiles();
        } catch (error) {
            this.handleSubmissionError(error);
        }
    }
    
    validateSubmission() {
        if (this.files.length === 0) {
            this.showFeedback('Пожалуйста, загрузите файлы', 'error');
            return false;
        }
        
        const configFiles = this.files.filter(f => this.getFileType(f.name) === 'config');
        const sourceFiles = this.files.filter(f => this.getFileType(f.name) === 'sources');
        
        if (configFiles.length === 0) {
            this.showFeedback('Необходим конфигурационный файл', 'error');
            return false;
        }
        
        if (sourceFiles.length === 0) {
            this.showFeedback('Необходимы исходные файлы Verilog', 'error');
            return false;
        }
        
        return true;
    }
    
    async submitFiles() {
        this.setLoadingState(true);
        
        const formData = new FormData();
        this.files.forEach(file => formData.append('files', file));
        
        const response = await fetch(this.url_api_update, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            this.handleSubmissionSuccess(data);
        } else {
            throw new Error(data.error || 'Ошибка при загрузке файлов');
        }
    }
    
    handleSubmissionSuccess(data) {
        this.showFeedback('Файлы загружены! Перенаправляем...', 'success');
        window.location.href = `/${data.run_id}`;
    }
    
    handleSubmissionError(error) {
        this.showFeedback(`Ошибка: ${error.message}`, 'error');
        this.setLoadingState(false);
    }
    
    setLoadingState(loading) {
        if (loading) {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '⏳ Загрузка и проверка файлов...';
        } else {
            this.updateSubmitButton();
            this.submitBtn.textContent = 'Запустить обработку данных';
        }
    }
    
    showFeedback(message, type) {
        this.feedback.textContent = message;
        this.feedback.className = `file-uploader__feedback file-uploader__feedback--${type}`;
    }
    
    hideFeedback() {
        this.feedback.style.display = 'none';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

