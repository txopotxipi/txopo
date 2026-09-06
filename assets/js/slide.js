// Array de imágenes para el carrusel de Navidad
var i = 0;
var images = [];
var time = 3000; // 3 segundos entre imágenes

// Lista de imágenes navideñas
images[0] = "fotosnavidad/IMG_20211126_192855.jpg";
images[1] = "fotosnavidad/IMG_20211128_192819.jpg";
images[2] = "fotosnavidad/IMG_20211128_193404.jpg";
images[3] = "fotosnavidad/IMG_20211128_194232.jpg";
images[4] = "fotosnavidad/IMG_20211128_195018.jpg";
images[5] = "fotosnavidad/IMG_20211222_180106.jpg";
images[6] = "fotosnavidad/IMG20211127185615.jpg";
images[7] = "fotosnavidad/IMG20211127190032.jpg";
images[8] = "fotosnavidad/IMG20211127190547.jpg";
images[9] = "fotosnavidad/IMG20211127192022 (1).jpg";
images[10] = "fotosnavidad/IMG20211127195017.jpg";
images[11] = "fotosnavidad/IMG20211128201518.jpg";
images[12] = "fotosnavidad/IMG20211203193838.jpg";
images[13] = "fotosnavidad/IMG20211207183646 (1).jpg";
images[14] = "fotosnavidad/IMG20211207192448.jpg";
images[15] = "fotosnavidad/IMG20211210191452.jpg";
images[16] = "fotosnavidad/IMG20211211194840.jpg";
images[17] = "fotosnavidad/IMG20211211202308.jpg";
images[18] = "fotosnavidad/IMG20211212185518.jpg";
images[19] = "fotosnavidad/IMG20211212190555.jpg";
images[20] = "fotosnavidad/IMG20211216185206.jpg";
images[21] = "fotosnavidad/IMG20211217211313.jpg";
images[22] = "fotosnavidad/IMG20211222180841.jpg";
images[23] = "fotosnavidad/IMG20211222185046.jpg";
images[24] = "fotosnavidad/PANO_20211211_194747.vr.jpg";

// Función para cambiar la imagen mostrada
function changeImg() {
    document.slide.src = images[i];
    if (i < images.length - 1) {
        i++;
    } else {
        i = 0;
    }
    setTimeout("changeImg()", time);
}

// Iniciar el carrusel cuando la página termine de cargar
window.onload = changeImg;