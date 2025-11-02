document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const helpSearch = document.getElementById('helpSearch');
    const navLinks = document.querySelectorAll('.sidebar__link');
    const contentSections = document.querySelectorAll('.main__section');
    
    // Поиск по документации
    helpSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        const highlights = document.querySelectorAll('.sidebar__search--highlight');
        
        // Удаляем предыдущие подсветки
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });
        
        // Показываем/скрываем секции
        contentSections.forEach(section => {
            const text = section.textContent.toLowerCase();
            const hasMatch = text.includes(searchTerm);
            
            section.classList.toggle('.main__section--hidden', !hasMatch && searchTerm.length > 1);
            
            // Подсветка найденного текста
            if (hasMatch && searchTerm.length > 1) {
                highlightText(section, searchTerm);
            }
        });
    });
    
    function highlightText(element, searchTerm) {
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            const parent = node.parentNode;
            if (parent.nodeName === 'SCRIPT' || parent.nodeName === 'STYLE') continue;
            
            const text = node.textContent;
            const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
            const newText = text.replace(regex, '<mark class="sidebar__search--highlight">$1</mark>');
            
            if (newText !== text) {
                const newElement = document.createElement('span');
                newElement.innerHTML = newText;
                parent.replaceChild(newElement, node);
            }
        }
    }
    
    // Навигация по разделам
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Обновляем активную ссылку
            navLinks.forEach(l => l.classList.remove('sidebar__link--active'));
            this.classList.add('sidebar__link--active');
            
            // Прокручиваем к разделу
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetSection.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Кнопка "Наверх"
    const backToTop = document.getElementById('backToTop');
    // Автоматическое обновление активной ссылки при прокрутке
    function updateActiveNavLink() {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const scrollPosition = window.pageYOffset + headerHeight + 100;
        
        let currentSection = '';
        
        contentSections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                currentSection = '#' + section.getAttribute('id');
            }
        });
        
        if (currentSection) {
            navLinks.forEach(link => {
                link.classList.remove('sidebar__link--active');
                if (link.getAttribute('href') === currentSection) {
                    link.classList.add('sidebar__link--active');
                }
            });
        }
    }
    
    window.addEventListener('scroll', updateActiveNavLink);
    
    // Инициализация
    updateActiveNavLink();
});
