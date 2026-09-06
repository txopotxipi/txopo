var swiper = new Swiper('.swiper-container', {
  // Opciones del slider
  slidesPerView: 1,
  spaceBetween: 30,
  centeredSlides: true,
  loop: true, // Permite que el slider se reinicie al llegar a la última imagen
  autoplay: {
    delay: 3000, // Tiempo en milisegundos entre cada slide
    disableOnInteraction: false, // Permite que el autoplay continúe incluso si el usuario interactúa con el slider
  },
  pagination: {
    el: '.swiper-pagination',
    clickable: true,
  },
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },
});