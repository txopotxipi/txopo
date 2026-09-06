// Generar slides
function generarSlide(imagen) {

  return `<div class="swiper-slide">
            <img src="${imagen}" loading="lazy">
          </div>`;

}

// Inicializar slider
function initSlider() {

  var imagenes = [];
  
  for(var i = 1; i <= 64; i++ ) {
    imagenes.push('../fotos/' + i + '.jpg');
  }

  imagenes.forEach(imagen => {

    var slide = generarSlide(imagen);
    
    document.querySelector('.swiper-wrapper').innerHTML += slide;

  });

}


// Inicializar plugin Swiper
initSlider();

var swiper = new Swiper('.swiper', {

  slidesPerView: 1,
  spaceBetween: 30,
  centeredSlides: true,

  lazy: true,

  pagination: {
    el: '.swiper-pagination',    
    clickable: true
  },

  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },

  autoplay: {
    delay: 3000,
    stopOnLastSlide: false,
    disableOnInteraction: false
  }

});

window.addEventListener('resize', function(){swiper.update(); 
});




