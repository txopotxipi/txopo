document.addEventListener('DOMContentLoaded', function() {
    const galeriaContainer = document.getElementById('imagenes');
    const sliderContainer = document.getElementById('slider');
    const sliderImage = document.getElementById('sliderImage');
    const cerrarSlider = document.getElementById('cerrarSlider');
    const prevImage = document.getElementById('prevImage');
    const nextImage = document.getElementById('nextImage');
    const playPauseSlider = document.getElementById('playPauseSlider');
    const videoContainer = document.getElementById('videoContainer');
    const tituloAnimado = document.getElementById('tituloAnimado');
    const menuToggle = document.getElementById('menuToggle');
    const mainNav = document.getElementById('mainNav');

    let currentImageIndex = 0;
    let images = [];
    let sliderInterval;
    let isPlaying = false;

    const titulo = "La Verbena Gallega";
    let i = 0;
    const velocidadEscritura = 100;

    function escribirTitulo() {
        if (i < titulo.length) {
            tituloAnimado.innerHTML += titulo.charAt(i);
            i++;
            setTimeout(escribirTitulo, velocidadEscritura);
        } else {
            gsap.to(tituloAnimado, {
                duration: 0.5,
                textShadow: "0 0 10px rgba(255,255,255,0.8)",
                yoyo: true,
                repeat: -1
            });
        }
    }

    escribirTitulo();

    menuToggle.addEventListener('click', () => {
        mainNav.classList.toggle('active');
        menuToggle.classList.toggle('active');
    });

    mainNav.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mainNav.classList.remove('active');
            menuToggle.classList.remove('active');
        });
    });

    for (let i = 1; i <= 171; i++) {
        const img = document.createElement('img');
        img.src = `fotos/${i}.jpg`;
        img.alt = `Imagen ${i}`;
        img.loading = 'lazy';
        img.addEventListener('click', () => iniciarSlider(i - 1));
        galeriaContainer.appendChild(img);
        images.push(img);
    }

    function iniciarSlider(index) {
        currentImageIndex = index;
        sl

iderContainer.style.display = 'flex';
        mostrarImagen(currentImageIndex);
        isPlaying = true;
        actualizarBotonPlayPause();
        iniciarRotacionAutomatica();
    }

    function mostrarImagen(index) {
        gsap.to(sliderImage, {
            opacity: 0,
            duration: 0.2,
            onComplete: () => {
                sliderImage.src = images[index].src;
                sliderImage.alt = images[index].alt;
                gsap.to(sliderImage, {
                    opacity: 1,
                    duration: 0.2
                });
            }
        });
    }

    function iniciarRotacionAutomatica() {
        detenerRotacionAutomatica();
        sliderInterval = setInterval(() => {
            if (isPlaying) {
                currentImageIndex = (currentImageIndex + 1) % images.length;
                mostrarImagen(currentImageIndex);
            }
        }, 3000);
    }

    function detenerRotacionAutomatica() {
        clearInterval(sliderInterval);
    }

    function actualizarBotonPlayPause() {
        playPauseSlider.innerHTML = isPlaying ? '❚❚' : '►';
    }

    cerrarSlider.onclick = () => {
        sliderContainer.style.display = 'none';
        detenerRotacionAutomatica();
    };

    prevImage.onclick = () => {
        currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
        mostrarImagen(currentImageIndex);
    };

    nextImage.onclick = () => {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        mostrarImagen(currentImageIndex);
    };

    playPauseSlider.onclick = () => {
        isPlaying = !isPlaying;
        actualizarBotonPlayPause();
        if (isPlaying) {
            iniciarRotacionAutomatica();
        } else {
            detenerRotacionAutomatica();
        }
    };

    const videoIds = [
        'a3cM1hIjDvI', 'oHDBp7Fe88U', 'V-4NgdgkDKo', 'ie7Xymq73kg', 'LwtAI_RyJfQ',
        '9GvPZG522U4', 'O9ABOgdPvW8', 'GCZ1qbqCKuo', '4aWs_ITQEMI', '4aWs_ITQEMI',
        'Hq3-c04jWrA', 'r1zmB0AYyGM', 'l6nuqKzFCxQ', 'RjbFVYZTE7c', 'RGLIBehWW0Y',
        'OKP9czosLjo', 'r2refvZq1v4', 'RFvxMzhrI6I', 'bkkyQTZxCmM', 'sMVq385MASE',
        'L4R33LL38zY', 'fOr1P4Zh-yE', 'Q07WbSDbV5Q', 'W9Bco7XnLP4', 'r_QrB9MzYZQ',
        'cMH8nvV4FCg', 'Iba4b5Z_zWE'
    ];

    videoIds.forEach(id => {
        const videoWrapper = document.createElement('div');
        videoWrapper.className = 'video-wrapper';
        videoWrapper.innerHTML = `
            <iframe width="560" height="315" src="https://www.youtube.com/embed/${id}" 
            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
        `;
        videoContainer.appendChild(videoWrapper);
    });

    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', entry.target.dataset.animation);
                observer.unobserve(entry.target);
            }
        });
    };

    const observer = new IntersectionObserver(animateOnScroll, { threshold: 0.1 });

    document.querySelectorAll('.animate__animated').forEach(element => {
        observer.observe(element);
    });

    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        document.body.style.backgroundPositionY = -(scrolled * 0.5) + 'px';
    });
});