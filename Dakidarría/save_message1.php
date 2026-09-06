<?php
// Establece la zona horaria a la de España
date_default_timezone_set('Europe/Madrid');
header('Content-Type: application/json');

// Función para sanitizar la entrada
function sanitize_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

// Comprueba si la solicitud es POST
if ($_SERVER["REQUEST_METHOD"] != "POST") {
    echo json_encode(["success" => false, "message" => "Método de solicitud no válido"]);
    exit();
}

$servername = "sql204.epizy.com";
$username = "epiz_30488727";
$password = "j2rng5bv";
$dbname = "epiz_30488727_db_contact";

// Crear la conexión
$conn = new mysqli($servername, $username, $password, $dbname);

// Verificar la conexión
if ($conn->connect_error) {
    error_log("Connection failed: " . $conn->connect_error);
    echo json_encode(["success" => false, "message" => "Error de conexión a la base de datos"]);
    exit();
}

// Obtener y sanitizar los datos del formulario
$nombre = sanitize_input($_POST['nombre'] ?? '');
$email = sanitize_input($_POST['email'] ?? '');
$mensaje = sanitize_input($_POST['mensaje'] ?? '');
$created_at = date('Y-m-d H:i:s'); // Obtener la fecha y hora actual en la zona horaria de Madrid

// Validar los datos
if (empty($nombre) || empty($email) || empty($mensaje)) {
    echo json_encode(["success" => false, "message" => "Todos los campos son obligatorios"]);
    exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(["success" => false, "message" => "Formato de email no válido"]);
    exit();
}

// Preparar la consulta
$stmt = $conn->prepare("INSERT INTO messages_cascadas (name, email, message, created_at) VALUES (?, ?, ?, ?)");
if ($stmt) {
    $stmt->bind_param("ssss", $nombre, $email, $mensaje, $created_at);

    // Ejecutar la consulta
    if ($stmt->execute()) {
        echo json_encode(["success" => true, "message" => "Mensaje enviado correctamente"]);
    } else {
        error_log("Error en la ejecución: " . $stmt->error);
        echo json_encode(["success" => false, "message" => "Error al enviar el mensaje"]);
    }

    // Cerrar la consulta
    $stmt->close();
} else {
    error_log("Error en la preparación de la consulta: " . $conn->error);
    echo json_encode(["success" => false, "message" => "Error al procesar el mensaje"]);
}

// Cerrar la conexión
$conn->close();
?>