// script.js
const sliderContainer = document.querySelector('.slider__container');
const sliderButtonPrev = document.querySelector('.slider__button--prev');
const sliderButtonNext = document.querySelector('.slider__button--next');
const sliderButtonStop = document.querySelector('.slider__button--stop');

// Creamos un array con las imágenes del slider
const images = [];
for (let i = 1; i <= 35; i++) {
  images.push(`../fotos/${i}.jpg`);
}

// Función para mostrar la imagen actual
function showCurrentImage() {
  sliderContainer.innerHTML = ''; // Limpiamos el contenedor antes de agregar la nueva imagen
  const img = document.createElement('img');
  img.src = images[index];
  sliderContainer.appendChild(img);
}

// Variables para controlar el slider
let index = 0;
let timer = null;

// Función para mover el slider a la izquierda
function moveLeft() {
  index--;
  if (index < 0) {
    index = images.length - 1;
  }
  showCurrentImage();
}

// Función para mover el slider a la derecha
function moveRight() {
  index++;
  if (index >= images.length) {
    index = 0;
  }
  showCurrentImage();
}

// Función para detener o reiniciar el slider
function toggleSlider() {
  if (timer) {
    clearInterval(timer);
    timer = null;
    sliderButtonStop.textContent = 'Reiniciar'; // Cambia el texto del botón a 'Reiniciar'
  } else {
    timer = setInterval(moveRight, 5000);
    sliderButtonStop.textContent = 'Detener'; // Cambia el texto del botón a 'Detener'
  }
}

// Añadimos los eventos a los botones del slider
sliderButtonPrev.addEventListener('click', moveLeft);
sliderButtonNext.addEventListener('click', moveRight);
sliderButtonStop.addEventListener('click', toggleSlider);

// Iniciamos el slider automáticamente
timer = setInterval(moveRight, 5000);

// Reiniciamos el timer cuando se pulse un botón del slider
function resetTimer() {
  clearInterval(timer);
  timer = setInterval(moveRight, 5000);
}

// Mostramos la primera imagen al cargar la página
showCurrentImage();
