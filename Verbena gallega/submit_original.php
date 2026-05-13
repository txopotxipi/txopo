<?php
// Configuración de la base de datos
$servername = "sql204.epizy.com";
$username = "epiz_30488727";
$password = "j2rng5bv";
$dbname = "epiz_30488727_db_contact";

// Crear la conexión
$conn = new mysqli($servername, $username, $password, $dbname);

// Verificar conexión
if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

// Obtener datos del formulario
$nombre = filter_input(INPUT_POST, 'nombre', FILTER_SANITIZE_STRING);
$email = filter_input(INPUT_POST, 'email', FILTER_SANITIZE_EMAIL);
$mensaje = filter_input(INPUT_POST, 'mensaje', FILTER_SANITIZE_STRING);

// Validar datos
if (!$nombre || !$email || !$mensaje || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die("Por favor, complete todos los campos correctamente.");
}

// Preparar y ejecutar la consulta SQL
$sql = "INSERT INTO Verbena (nombre, email, mensaje) VALUES (?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("sss", $nombre, $email, $mensaje);

if ($stmt->execute()) {
    // Mostrar mensaje de éxito y redirigir después de 3 segundos
    echo "<div style='text-align: center; margin-top: 50px;'>
            <h2>¡Mensaje enviado correctamente!</h2>
            <p>Te devuelvo a la página principal en 3 segundos...</p>
          </div>
          <script>
            setTimeout(function(){
              window.location.href = 'index.html';
            }, 3000);
          </script>";
} else {
    echo "Error: " . $stmt->error;
}

$stmt->close();
$conn->close();
?>