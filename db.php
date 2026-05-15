<?php
//Configuración necesaria para acceder a la base de datos

$hostname="sql204.epizy.com";
$usuariodb="epiz_30488727";
$passworddb="j2rng5bv";
$dbname="epiz_30488727_db_contact";

$conectar = mysqli_connect($hostname, $usuariodb, $passworddb, $dbname);

if (!$conectar) {
    error_log("Error de conexión a la base de datos: " . mysqli_connect_error());
    die("Lo sentimos, ha ocurrido un error al conectar con la base de datos.");
}

mysqli_set_charset($conectar, 'utf8');
?>
