class DialogManager {
    constructor(dialogElement) {
        this.dialog = dialogElement;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        // Close dialog on backdrop click
        this.dialog.addEventListener('click', (e) => {
            if (e.target === this.dialog) {
                this.close();
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }
    
    open() {
        this.dialog.classList.add('dialog--open');
        this.isOpen = true;
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.dialog.classList.remove('dialog--open');
        this.isOpen = false;
        document.body.style.overflow = '';
    }
    
    setContent(title, message, type = 'info') {
        const titleElement = this.dialog.querySelector('.dialog__title');
        const bodyElement = this.dialog.querySelector('.dialog__body');
        
        if (titleElement) titleElement.textContent = title;
        if (bodyElement) bodyElement.innerHTML = message;
        
        // Set dialog type
        this.dialog.className = 'dialog';
        this.dialog.classList.add(`dialog--${type}`);
    }
}

// Usage example
const deleteDialog = new DialogManager(document.getElementById('deleteDialog'));

// Open confirmation dialog
function confirmDelete(folderName) {
    const message = `
        <p class="dialog__text">Вы уверены, что хотите удалить директорию <strong class="dialog__highlight">${folderName}</strong>?</p>
        <p class="dialog__warning">Это действие нельзя отменить. Все файлы в директории будут удалены безвозвратно.</p>
    `;
    
    deleteDialog.setContent('Подтверждение удаления', message, 'warning');
    deleteDialog.open();
    
    return new Promise((resolve) => {
        const confirmBtn = document.getElementById('confirmDelete');
        const cancelBtn = document.getElementById('cancelDelete');
        const closeBtn = document.getElementById('closeDialog');
        
        const cleanup = () => {
            confirmBtn.removeEventListener('click', onConfirm);
            cancelBtn.removeEventListener('click', onCancel);
            closeBtn.removeEventListener('click', onCancel);
        };
        
        const onConfirm = () => {
            cleanup();
            deleteDialog.close();
            resolve(true);
        };
        
        const onCancel = () => {
            cleanup();
            deleteDialog.close();
            resolve(false);
        };
        
        confirmBtn.addEventListener('click', onConfirm);
        cancelBtn.addEventListener('click', onCancel);
        closeBtn.addEventListener('click', onCancel);
    });
}
