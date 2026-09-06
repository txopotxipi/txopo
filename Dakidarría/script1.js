document.addEventListener("DOMContentLoaded", function() {
    // Inicializar AOS (Animate on Scroll)
    AOS.init({
        duration: 1000,
        once: true
    });

    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Lazy loading for images
    const lazyLoadImages = document.querySelectorAll("img.lazy");
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const image = entry.target;
                image.src = image.dataset.src;
                image.classList.remove("lazy");
                image.classList.add("loaded");
                observer.unobserve(image);
            }
        });
    });

    lazyLoadImages.forEach(image => imageObserver.observe(image));

    // Initialize lightbox
    lightbox.option({
        'resizeDuration': 200,
        'wrapAround': true,
        'disableScrolling': true
    });

    // Manejar la reproducción de videos
    document.querySelectorAll('.video-overlay').forEach(overlay => {
        overlay.addEventListener('click', function() {
            const wrapper = this.closest('.video-item');
            const iframe = wrapper.querySelector('iframe.lazy-video');
            
            if (iframe.src === '') {
                iframe.src = iframe.dataset.src;
            }
            
            this.style.display = 'none';
        });
    });

    // Lazy loading para videos
    const lazyVideos = document.querySelectorAll("iframe.lazy-video");
    const videoObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const video = entry.target;
                if (video.src === '') {
                    video.src = video.dataset.src.replace('autoplay=1', 'autoplay=0');
                }
                observer.unobserve(video);
            }
        });
    });

    lazyVideos.forEach(video => videoObserver.observe(video));

    // Form submission with AJAX
    const contactForm = document.getElementById('contactForm');
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('save_message.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                contactForm.reset();
            } else {
                showNotification("Error: " + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification("Hubo un error al enviar el formulario", 'error');
        });
    });

    // Notification function
    function showNotification(message, type) {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    // Parallax effect for header
    window.addEventListener('scroll', function() {
        const parallax = document.querySelector('.parallax-header');
        let scrollPosition = window.pageYOffset;
        parallax.style.backgroundPositionY = scrollPosition * 0.5 + 'px';
    });

    // Cerrar el menú al hacer clic en un enlace
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992) {  // Solo en dispositivos móviles
                navbarToggler.click();  // Simula un clic en el botón del menú para cerrarlo
            }
        });
    });

    // Add a scroll-to-top button
    const scrollTopButton = document.createElement('button');
    scrollTopButton.innerHTML = '&uarr;';
    scrollTopButton.setAttribute('id', 'scrollTopBtn');
    document.body.appendChild(scrollTopButton);

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollTopButton.style.display = 'block';
        } else {
            scrollTopButton.style.display = 'none';
        }
    });

    scrollTopButton.addEventListener('click', () => {
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
});

document.querySelectorAll('.video-item').forEach(item => {
    item.addEventListener('click', function() {
      const iframe = this.querySelector('iframe');
      const src = iframe.src;
      if (!src.includes('autoplay=1')) {
        iframe.src = src + '?autoplay=1';
      }
    });
  });