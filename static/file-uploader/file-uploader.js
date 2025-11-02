class FileUploader {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.fileInput = document.getElementById('jsonFile');
        this.runButton = document.getElementById('runButton');
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.fileInput.addEventListener('change', this.handleFileChange.bind(this));
        
        this.updateButtonState();
    }

    handleFileChange(e) {
        const file = e.target.files[0];
        const validation = this.validateFile(file);
        
        this.showFeedback(validation.message, validation.isValid ? 'success' : 'error');
        this.updateButtonState();
        
        if (file && validation.isValid) {
            this.showFilePreview(file);
        } else {
            this.hideFilePreview();
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const file = this.fileInput.files[0];
        const validation = this.validateFile(file);
        
        if (!validation.isValid) {
            this.showFeedback(validation.message, 'error');
            return;
        }

        this.setLoadingState(true);
        
        try {
            const result = await this.uploadToServer(file);
            this.showFeedback('Файл успешно обработан!', 'success');
            this.onUploadSuccess(result);
        } catch (error) {
            this.showFeedback(error.message, 'error');
        } finally {
            this.setLoadingState(false);
        }
    }

    validateFile(file) {
        if (!file) {
            return { isValid: false, message: 'Файл не выбран' };
        }
        
        if (!file.name.endsWith('.json')) {
            return { isValid: false, message: 'Только JSON файлы' };
        }
        
        if (file.size > 10 * 1024 * 1024) {
            return { isValid: false, message: 'Файл слишком большой (макс. 10MB)' };
        }
        
        return { isValid: true, message: 'Файл валиден' };
    }

    updateButtonState() {
        const file = this.fileInput.files[0];
        const validation = this.validateFile(file);
        const isLoading = this.runButton.classList.contains('button--loading');
        
        if (isLoading) {
            this.runButton.disabled = true;
            this.runButton.classList.add('button--disabled');
        } else if (validation.isValid) {
            this.runButton.disabled = false;
            this.runButton.classList.remove('button--disabled');
        } else {
            this.runButton.disabled = true;
            this.runButton.classList.add('button--disabled');
        }
    }

    setLoadingState(isLoading) {
        if (isLoading) {
            this.runButton.classList.add('button--loading');
            this.runButton.textContent = 'Обработка...';
        } else {
            this.runButton.classList.remove('button--loading');
            this.runButton.textContent = 'Запустить обработку данных';
        }
        this.updateButtonState();
    }

    showFilePreview(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        fileInfo.classList.add('file-uploader__preview--visible');
        
        document.getElementById('removeFile').addEventListener('click', () => {
            this.fileInput.value = '';
            this.hideFilePreview();
            this.updateButtonState();
            this.showFeedback('', 'info');
        });
    }

    hideFilePreview() {
        const fileInfo = document.getElementById('fileInfo');
        fileInfo.classList.remove('file-uploader__preview--visible');
    }

    async uploadToServer(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Ошибка загрузки');
        }

        return await response.json();
    }

    showFeedback(message, type) {
        const feedback = document.getElementById('validationMessage');
        feedback.textContent = message;
        feedback.className = `file-uploader__feedback`;
        
        if (message) {
            feedback.classList.add(`file-uploader__feedback--${type}`);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    onUploadSuccess(data) {
        console.log('Данные обработаны:', data);
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    const uploader = new FileUploader('uploadForm');
});

