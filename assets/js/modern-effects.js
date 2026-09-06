/* Modern Effects JS - Efectos interactivos adicionales para txopo */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Efecto de aparición gradual para las imágenes al hacer scroll
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                img.style.opacity = '1';
                img.style.transform = 'translateY(0)';
                observer.unobserve(img);
            }
        });
    }, observerOptions);

    // Aplicar a todas las imágenes en la galería
    document.querySelectorAll('.image.fit img').forEach(img => {
        img.style.opacity = '0';
        img.style.transform = 'translateY(20px)';
        imageObserver.observe(img);
    });

    // Efecto de parallax suave para la sección de portada
    const coverSection = document.querySelector('section.one.dark.cover');
    if (coverSection) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            if (scrollPosition < 1000) { // Solo aplicar en la parte superior
                coverSection.style.backgroundPositionY = scrollPosition * 0.5 + 'px';
            }
        });
    }

    // Efecto de resaltado para la navegación
    const navItems = document.querySelectorAll('#nav ul li a');
    navItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.querySelector('.icon').classList.add('fa-beat');
        });
        item.addEventListener('mouseleave', function() {
            this.querySelector('.icon').classList.remove('fa-beat');
        });
    });

    // Mejora para el formulario de contacto
    const formInputs = document.querySelectorAll('input, textarea');
    formInputs.forEach(input => {
        // Añadir clase cuando el input está enfocado
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        // Quitar clase cuando pierde el foco
        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.parentElement.classList.remove('input-focused');
            }
        });
    });

    // Efecto de hover para los enlaces de la lista de sitios
    const siteLinks = document.querySelectorAll('.alternativo');
    siteLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.color = '#e74c3c';
        });
        link.addEventListener('mouseleave', function() {
            this.style.color = '';
        });
    });

    // Animación para el botón de envío del formulario
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.2)';
        });
        submitButton.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    }
});