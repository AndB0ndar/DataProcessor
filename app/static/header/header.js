class MobileMenu {
    constructor() {
        this.menuToggle = document.querySelector('.header__menu-toggle');
        this.mainNav = document.querySelector('.header__nav');
        this.navLinks = document.querySelectorAll('.header__link');
        this.body = document.body;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        this.menuToggle.addEventListener('click', this.toggleMenu.bind(this));
        
        this.navLinks.forEach(link => {
            link.addEventListener('click', this.closeMenu.bind(this));
        });
        
        document.addEventListener('keydown', this.handleKeyPress.bind(this));
    }
    
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
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = new MobileMenu();
});
