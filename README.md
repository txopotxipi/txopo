# Txopo Txipi

Portada principal y archivo de viajes de Txopo Txipi.

La home se ha rehecho para funcionar como una entrada visual mas potente, ligera y totalmente responsive, manteniendo intactas las subwebs historicas de cada viaje para no romper el archivo existente.

## Produccion

La web publicada vive en:

- [https://txopo.lovestoblog.com](https://txopo.lovestoblog.com)

## Estructura util

- `index.html`: portada principal renovada.
- `assets/css/design-system.css`: sistema visual de la nueva home.
- `assets/js/sites-data.js`: inventario de destinos y seleccion destacada.
- `assets/js/app.js`: interacciones, filtros, efectos estacionales ligeros y validacion del formulario.
- `contact.php`, `get_token.php`, `csrf_utils.php`, `db.php`: backend minimo del formulario de contacto.
- `config/db_config.php`: credenciales locales de la base de datos. Esta ruta esta ignorada por git.
- `[Destino]/index.html`: subwebs historicas de viajes, rutas, ciudades y momentos especiales.

## Objetivos de la nueva home

- Priorizar una experiencia mobile-first sin perder presencia en portatil y escritorio.
- Reducir ruido visual heredado del tema antiguo.
- Mejorar el descubrimiento del archivo mediante busqueda y filtros.
- Sustituir nieve, Grinch y carrusel navideno por una atmosfera primaveral mas ligera.
- Mantener compatibilidad con el formulario PHP existente.

## Limpieza aplicada

- Eliminados los efectos navidenos y el carrusel estacional de la portada.
- Eliminado el volcado `contenido_archivos.txt`, que no participaba en el funcionamiento de la web.
- Eliminado el paquete de la plantilla antigua que ya no se usaba en ninguna pagina (`main.css`, jQuery y utilidades asociadas).
- Conservadas las subwebs y cualquier recurso dudoso hasta verificar que no afecta al archivo historico.

## Notas

- Algunas subwebs siguen usando maquetas antiguas o estructuras de galeria diferentes. La portada nueva ya no depende de ellas para ofrecer una experiencia consistente.
- Si se quiere una segunda fase, lo natural es normalizar plantillas y compresion de imagenes dentro de las subwebs mas visitadas.
