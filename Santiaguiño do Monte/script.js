// Array de imágenes
const imageArray = [
  'fotos/1.jpg',
  'fotos/2.jpg',
  'fotos/3.jpg',
  'fotos/4.jpg',
  'fotos/5.jpg',
  'fotos/6.jpg',
  'fotos/7.jpg',
  'fotos/8.jpg',
  'fotos/9.jpg',
  'fotos/10.jpg',
  'fotos/11.jpg',
  'fotos/12.jpg',
  'fotos/13.jpg',
  'fotos/14.jpg'
];

// Array para precargar imágenes 
const images = []; 

// Precargar todas las imágenes  
imageArray.forEach(image => {
  const img = new Image();
  img.src = image;
  images.push(img);
});

// Imagen actual
let currentIndex = 0;

// Cambiar imagen cada 5 segundos
setInterval(() => {
  document.querySelector('.photo img').src = images[currentIndex].src;
  
  currentIndex++;
  if(currentIndex >= images.length) {
    currentIndex = 0; 
  }
}, 5000); 

// Botón para detener el slider
const stopButton = document.querySelector('#stop');

let intervalId; 

stopButton.addEventListener('click', () => {
  clearInterval(intervalId); 
  
  // Reanudar slider después de 5 segundos
  intervalId = setTimeout(() => {
    intervalId = setInterval(() => {
      // Código para cambiar imagen  
    }, 5000);
  }, 5000);
});