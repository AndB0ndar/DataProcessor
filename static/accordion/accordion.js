// Accordion functionality with icon change
document.addEventListener('DOMContentLoaded', function() {
    const accordionItems = document.querySelectorAll('.accordion__item');
    
    accordionItems.forEach(item => {
        const trigger = item.querySelector('.accordion__trigger');
        const icon = item.querySelector('.accordion__icon');
        
        trigger.addEventListener('click', () => {
            const isActive = item.classList.contains('accordion__item--active');
            
            // Close all items and reset icons
            accordionItems.forEach(otherItem => {
                const otherIcon = otherItem.querySelector('.accordion__icon');
                otherItem.classList.remove('accordion__item--active');
                otherIcon.textContent = '+'; // Reset to plus
            });
            
            // Open current item if it wasn't active
            if (!isActive) {
                item.classList.add('accordion__item--active');
                icon.textContent = '-'; // Change to minus
            }
        });
    });
});
