# Romería de San Ramón – Sitio estático

Sitio web estático, moderno y responsive para presentar la romería: galería con lightbox, carrusel, partículas en el hero, animaciones y botón de WhatsApp. Funciona en hosting gratuito (InfinityFree) usando CDNs.

## Estructura

- `index.html`: página principal
- `css/styles.css`: estilos personalizados
- `js/scripts.js`: inicializaciones (AOS, GLightbox, tsParticles, Swiper, VanillaTilt, back-to-top, WhatsApp)
- `fotos/`: imágenes del hero, carrusel y galería (`1.jpg` a `8.jpg`)

## Requisitos

- Hosting estático (probado en InfinityFree). No requiere PHP ni base de datos.
- Acceso a CDNs (jsDelivr/unpkg): Bootstrap, AOS, GLightbox, Swiper, tsParticles, VanillaTilt.

## Despliegue en InfinityFree

1. En el Panel de Control, abre el Administrador de Archivos o usa FTP.
2. Sube todo el contenido del proyecto a `htdocs/` del dominio/subdominio.
3. Estructura final en servidor:
   - `htdocs/index.html`
   - `htdocs/css/styles.css`
   - `htdocs/js/scripts.js`
   - `htdocs/fotos/1.jpg` … `htdocs/fotos/8.jpg`
4. Abre tu URL pública y verifica que cargan estilos/JS (sin errores de CDN bloqueado).

Notas:

- Respeta mayúsculas/minúsculas en rutas (`fotos/1.jpg` ≠ `Fotos/1.jpg`).
- Si algún CDN está bloqueado temporalmente, vuelve a cargar o prueba otra red.

## Personalización y mantenimiento

### 1) Cambiar fotos

- Sustituye imágenes en `fotos/` con el mismo nombre (`1.jpg`…`8.jpg`) o edita las rutas en `index.html` (carrusel y galería).
- Optimiza imágenes antes de subir (≈ 200–300 KB por foto recomendado).

### 2) Editar textos

- Secciones: `Acerca de`, `Banda`, `Contacto` en `index.html`.
- Cambia encabezados y párrafos directamente en el HTML.

### 3) WhatsApp flotante

- En `index.html`, busca el enlace con clase `wa-float` y ajusta:
  - `data-wa-phone="34XXXXXXXXX"` (tu número con prefijo país, sin `+`).
  - `data-wa-text="Mensaje de saludo"`.
  - `data-wa-open="9"` y `data-wa-close="21"` para horario (24h locales).
- El botón se oculta fuera de horario automáticamente (lógica en `js/scripts.js`).

### 4) Metadatos sociales y favicon

- En el `<head>` de `index.html`:
  - `meta name="description"` y `og:description`.
  - `meta property="og:image"` (ideal 1200×630, por ejemplo `fotos/og.jpg`).
  - `link rel="icon" href="fotos/1.jpg"` (puedes usar `.ico`/`.png`).

### 5) Ajustes visuales

- Hero: fondo en `css/styles.css` (`.hero { background: url('../fotos/1.jpg') ... }`).
- Carrusel (Swiper): breakpoints y autoplay en `js/scripts.js`.
- Animaciones AOS: controla efectos con `data-aos` en `index.html`.

## Solución de problemas

- No carga CSS/JS externo: revisa plan/CDNs y bloqueadores.
- Imágenes rotas: revisa rutas y mayúsculas/minúsculas; confirma archivos en `/fotos/`.
- Lightbox no abre: confirma clase `glightbox` y orden de scripts.
- Partículas no se ven: comprueba `<div id="heroParticles"></div>` dentro de `#inicio`.
- WhatsApp no aparece: puede estar fuera de horario; ajusta `data-wa-open`/`data-wa-close`.

## Créditos de librerías

Bootstrap 5, AOS, GLightbox, Swiper, tsParticles, VanillaTilt (CDN: jsDelivr/unpkg).

## Licencia

Proyecto de ejemplo para romería. Usa tus propias imágenes y respeta sus derechos.
