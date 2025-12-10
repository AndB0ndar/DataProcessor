class MobileMenu {
    constructor(config = {}) {
        this.menuToggle = document.querySelector('.header__menu-toggle');
        this.mainNav = document.querySelector('.header__nav');
        this.body = document.body;
        this.resultsItem = document.getElementById('results-nav-item');
        this.uploadItem = document.getElementById('upload-nav-item');
        this.pollStatusUrl = config.pollStatusUrl || null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.startStatusPolling();
    }
    
    bindEvents() {
        if (!this.menuToggle) return;
        
        this.menuToggle.addEventListener('click', () => this.toggleMenu());
        
        document.querySelectorAll('.header__link').forEach(link => {
            link.addEventListener('click', () => this.closeMenu());
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMenuOpen()) this.closeMenu();
        });
    }
    
    startStatusPolling() {
        if (!this.pollStatusUrl) return;
        
        const checkStatus = async () => {
            try {
                const response = await fetch(this.pollStatusUrl);
                if (!response.ok) return;
                
                const data = await response.json();
                
                if (data.is_finished) {
                    this.stopPolling();
                    this.updateMenu();
                }
            } catch (error) {
                console.error('Status polling error:', error);
                this.stopPolling();
            }
        };
        
        this.pollingInterval = setInterval(checkStatus, 5000);  // 5s
        checkStatus();
    }
    
    updateMenu() {
        if (this.resultsItem) {
            this.resultsItem.classList.remove('header__item--hidden');
        }
        if (this.uploadItem) {
            this.uploadItem.classList.remove('header__item--hidden');
        }
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    toggleMenu() {
        const isExpanded = this.menuToggle.getAttribute('aria-expanded') === 'true';
        this.menuToggle.setAttribute('aria-expanded', !isExpanded);
        this.mainNav.classList.toggle('header__nav--mobile');
        this.body.classList.toggle('page__menu--open');
    }
    
    closeMenu() {
        this.menuToggle.setAttribute('aria-expanded', 'false');
        this.mainNav.classList.remove('header__nav--mobile');
        this.body.classList.remove('page__menu--open');
    }
    
    isMenuOpen() {
        return this.mainNav.classList.contains('header__nav--mobile');
    }
    
    updateConfig(newConfig) {
        if (newConfig.pollStatusUrl !== undefined) {
            this.pollStatusUrl = newConfig.pollStatusUrl;
            this.stopPolling();
            this.startStatusPolling();
        }
    }
    
    destroy() {
        this.stopPolling();
        
        if (this.menuToggle) {
            this.menuToggle.removeEventListener('click', this.toggleMenu);
        }
        
        document.querySelectorAll('.header__link').forEach(link => {
            link.removeEventListener('click', this.closeMenu);
        });
        
        document.removeEventListener('keydown', this.handleKeyPress);
    }
}
