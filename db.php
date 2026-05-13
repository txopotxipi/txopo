<?php
// Configuración necesaria para acceder a la base de datos

// Cargar credenciales desde archivo protegido (en .gitignore)
$config_file = __DIR__ . '/config/db_config.php';
if (file_exists($config_file)) {
    require_once $config_file;
} else {
    // Fallback: credenciales por defecto para producción
    // IMPORTANTE: Crear config/db_config.php con las credenciales reales
    define('DB_HOST', 'sql204.epizy.com');
    define('DB_USER', 'epiz_30488727');
    define('DB_PASS', 'j2rng5bv');
    define('DB_NAME', 'epiz_30488727_db_contact');
}

// Crear conexión con manejo de errores mejorado
$conectar = mysqli_connect(DB_HOST, DB_USER, DB_PASS, DB_NAME);

// Verificar conexión sin mostrar mensajes de depuración en producción
if (!$conectar) {
    // Registrar el error en un archivo de log en lugar de mostrarlo
    error_log('Error de conexión a la base de datos: ' . mysqli_connect_error());
    // Mostrar un mensaje genérico al usuario
    die("Lo sentimos, ha ocurrido un error al conectar con la base de datos.");
}

// Establecer el conjunto de caracteres de la conexión
mysqli_set_charset($conectar, 'utf8');

?>