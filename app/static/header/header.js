class MobileMenu {
    constructor() {
        this.menuToggle = document.querySelector('.header__menu-toggle');
        this.mainNav = document.querySelector('.header__nav');
        this.navLinks = document.querySelectorAll('.header__link');
        this.body = document.body;
        this.pollingInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.startStatusPolling();
    }
    
    bindEvents() {
        this.menuToggle.addEventListener('click', this.toggleMenu.bind(this));
        
        this.navLinks.forEach(link => {
            link.addEventListener('click', this.closeMenu.bind(this));
        });
        
        document.addEventListener('keydown', this.handleKeyPress.bind(this));
    }
    
    // Новый метод для опроса статуса
    startStatusPolling() {
        // Проверяем, есть ли текущий запуск и не завершен ли он
        if (window.currentRun && !window.currentRun.isFinished) {
            // Опрашиваем каждые 3 секунды
            this.pollingInterval = setInterval(() => {
                this.checkRunStatus();
            }, 3000);
        }
    }
    
    async checkRunStatus() {
        try {
            const response = await fetch(`/api/run/${window.currentRun.id}/status`);
            const data = await response.json();
            
            if (data.is_finished && !window.currentRun.isFinished) {
                // Останавливаем опрос
                clearInterval(this.pollingInterval);
                // Обновляем глобальную переменную
                window.currentRun.isFinished = true;
                // Обновляем навигацию
                this.updateNavigation();
            }
        } catch (error) {
            console.error('Error checking run status:', error);
        }
    }
    
    updateNavigation() {
        // Создаем новый элемент для результатов
        const resultsItem = document.createElement('li');
        resultsItem.className = 'header__item';
        
        const resultsLink = document.createElement('a');
        resultsLink.href = window.currentRun.resultsUrl;
        resultsLink.className = 'header__link';
        resultsLink.textContent = 'Результаты';
        
        // Добавляем обработчик для закрытия меню
        resultsLink.addEventListener('click', this.closeMenu.bind(this));
        
        resultsItem.appendChild(resultsLink);
        
        // Находим контейнер меню и добавляем новый элемент
        const menu = document.querySelector('.header__menu');
        const logsItem = document.querySelector('a[href*="logs"]').closest('.header__item');
        
        if (logsItem && logsItem.nextSibling) {
            menu.insertBefore(resultsItem, logsItem.nextSibling);
        } else {
            menu.appendChild(resultsItem);
        }
        
        // Показываем уведомление пользователю (опционально)
        this.showResultsNotification();
    }
    
    showResultsNotification() {
        // Можно добавить всплывающее уведомление
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        `;
        notification.textContent = 'Результаты готовы!';
        
        document.body.appendChild(notification);
        
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Остальные методы остаются без изменений
    toggleMenu() {
        const isExpanded = this.menuToggle.getAttribute('aria-expanded') === 'true';
        
        this.menuToggle.setAttribute('aria-expanded', !isExpanded);
        this.mainNav.classList.toggle('header__nav--mobile');
        this.body.classList.toggle('page__menu--open');
    }
    
    openMenu() {
        this.menuToggle.setAttribute('aria-expanded', 'true');
        this.mainNav.classList.add('header__nav--mobile');
        this.body.classList.add('page__menu--open');
    }
    
    closeMenu() {
        this.menuToggle.setAttribute('aria-expanded', 'false');
        this.mainNav.classList.remove('header__nav--mobile');
        this.body.classList.remove('page__menu--open');
    }
    
    handleKeyPress(event) {
        if (event.key === 'Escape' && this.isMenuOpen()) {
            this.closeMenu();
        }
    }
    
    isMenuOpen() {
        return this.mainNav.classList.contains('header__nav--mobile');
    }
    
    destroy() {
        this.menuToggle.removeEventListener('click', this.toggleMenu.bind(this));
        this.navLinks.forEach(link => {
            link.removeEventListener('click', this.closeMenu.bind(this));
        });
        document.removeEventListener('keydown', this.handleKeyPress.bind(this));
        
        // Останавливаем опрос при уничтожении
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = new MobileMenu();
});
