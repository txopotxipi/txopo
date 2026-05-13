<?php
// Incluir archivo de configuración para reutilizar credenciales
require_once('db.php');

try {
    // Usar constantes definidas en db.php
    $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME;
    $options = [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ];
    $bd = new PDO($dsn, DB_USER, DB_PASS, $options);

    $mitz = "Europe/Madrid";
    $tz = (new DateTime('now', new DateTimeZone($mitz)))->format('P');

    // Usar consulta preparada para mayor seguridad
    $stmt = $bd->prepare("SET time_zone = ?");
    $stmt->execute([$tz]);

    $stmt = $bd->query("SELECT NOW() AS mifecha");
    $q = $stmt->fetch();

    echo "Esta es la hora en " . htmlspecialchars($mitz) . " en la base de datos: ";
    echo htmlspecialchars($q['mifecha']);

} catch (PDOException $e) {
    // Registrar el error en un archivo de log en lugar de mostrarlo
    error_log('Error en fechalocal.php: ' . $e->getMessage());
    echo "Ha ocurrido un error al obtener la fecha.";
}
?>