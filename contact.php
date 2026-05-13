<?php
    // Verificación CSRF
    require_once 'csrf_utils.php';
    
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $token = isset($_POST['csrf_token']) ? $_POST['csrf_token'] : '';
        if (!verify_csrf_token($token)) {
            header("refresh:3;url=/");
            die('<p style="text-align:center;padding:50px;font-family:sans-serif;"><strong>Error de seguridad:</strong> Token de verificación inválido. Serás redirigido a la página principal.</p>');
        }
    }
    
    include_once('db.php');
    // Función para sanitizar entradas
    function sanitize_input($data) {
        $data = trim($data);
        $data = stripslashes($data);
        $data = htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
        return $data;
    }
    
    // Validar y sanitizar entradas
    $visitor_name = isset($_POST['visitor_name']) ? sanitize_input($_POST['visitor_name']) : '';
    $visitor_email = isset($_POST['visitor_email']) ? sanitize_input($_POST['visitor_email']) : '';
    $visitor_message = isset($_POST['visitor_message']) ? sanitize_input($_POST['visitor_message']) : '';
    $email_title = isset($_POST['email_title']) ? sanitize_input($_POST['email_title']) : '';
    
    $concerned_department = null;
    if(isset($_POST['concerned_department'])){
        $concerned_department = sanitize_input($_POST['concerned_department']);
    }
    
    // Validación básica
    $errors = [];
    if(empty($visitor_name)) {
        $errors[] = "El nombre es obligatorio";
    }
    if(empty($visitor_email) || !filter_var($visitor_email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Email no válido";
    }
    if(empty($visitor_message)) {
        $errors[] = "El mensaje es obligatorio";
    }
    
    if(empty($errors)) {
        $visita = $visitor_name; // Ya está sanitizado, no necesitamos utf8_encode
        date_default_timezone_set("Europe/Madrid");
        $fecha = date('Y-m-d H:i:s');
        
        // Usar consultas preparadas para prevenir inyección SQL
        $stmt = mysqli_prepare($conectar, "INSERT INTO `mensajes` (`id`, `visitor_name`, `visitor_email`, `visitor_message`, `email_title`, `fecha`) VALUES (NULL, ?, ?, ?, ?, ?)");
        mysqli_stmt_bind_param($stmt, "sssss", $visitor_name, $visitor_email, $visitor_message, $email_title, $fecha);
        
        if (mysqli_stmt_execute($stmt)) {
            echo "<p><h1>Gracias por tus pensamientos, $visita. Serán enviados a las estrellas, ellas sabrán darte una respuesta.</h1></p>";
            mysqli_stmt_close($stmt);
        } else {
            echo "<p>Ha ocurrido un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.</p>";
        }
    } else {
        echo "<p>Por favor, corrige los siguientes errores:</p><ul>";
        foreach($errors as $error) {
            echo "<li>$error</li>";
        }
        echo "</ul>";
    }
    
    mysqli_close($conectar);
    // Establecer el encabezado de actualización utilizando PHP.
    header("refresh:5;url=/");
?>