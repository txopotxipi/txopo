window.addEventListener('DOMContentLoaded', function() {
  const grid = document.getElementById('grid');
  const modal = document.getElementById('modal');
  const closeBtn = document.getElementById('close');
  const slideImg = document.getElementById('slide-img');
  const prevBtn = document.querySelector('.prev');
  const nextBtn = document.querySelector('.next');
  let currentIndex = 0;
  let images = [];

  // Carga las imágenes y sus rutas
  for (let i = 1; i <= 35; i++) {
    const img = new Image();
    img.src = `fotos/${i}.jpg`;
    img.alt = `Foto ${i}`;
    img.addEventListener('click', function() {
      openSlider(i);
    });
    grid.appendChild(img);
    images.push(img);
  }

  // Función para abrir el slider
  function openSlider(index) {
    currentIndex = index - 1;
    showSlide(currentIndex);
    modal.style.display = 'flex';
  }

  // Función para mostrar la imagen actual
  function showSlide(n) {
    currentIndex = (n + images.length) % images.length;
    slideImg.src = images[currentIndex].src;
    slideImg.alt = images[currentIndex].alt;
  }

  // Controles para el slider
  prevBtn.addEventListener('click', () => showSlide(currentIndex - 1));
  nextBtn.addEventListener('click', () => showSlide(currentIndex + 1));

  // Cierra el modal al hacer clic en la X
  closeBtn.addEventListener('click', function() {
    modal.style.display = 'none';
  });

  // Cierra el modal al hacer clic fuera del contenido
  window.addEventListener('click', function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
  });

  // Cierra el modal al presionar la tecla "Esc"
  window.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      modal.style.display = 'none';
    }
  });
});