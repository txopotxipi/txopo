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
  'fotos/14.jpg',
  'fotos/15.jpg',
  'fotos/16.jpg',
  'fotos/17.jpg',
  'fotos/18.jpg',
  'fotos/19.jpg',
  'fotos/20.jpg',
  'fotos/21.jpg',
  'fotos/22.jpg',
  'fotos/23.jpg',
  'fotos/24.jpg',
  'fotos/26.jpg',
  'fotos/27.jpg',
  'fotos/28.jpg',
  'fotos/29.jpg',
  'fotos/30.jpg', 
  'fotos/32.jpg',
  'fotos/35.jpg',
  'fotos/36.jpg',
  'fotos/37.jpg',
  'fotos/38.jpg',
  'fotos/39.jpg',
  'fotos/40.jpg',
  'fotos/41.jpg',
  'fotos/42.jpg',
  'fotos/43.jpg',
  'fotos/44.jpg',
  'fotos/45.jpg',
  'fotos/46.jpg'  
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
}, 2000); 

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