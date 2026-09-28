<?php
require_once 'csrf_utils.php';

function render_response_page($title, $message, $variant = 'success', $refreshSeconds = 5) {
    $safeTitle = htmlspecialchars($title, ENT_QUOTES, 'UTF-8');
    $icon = $variant === 'success' ? '&#9993;' : '!';

    header("refresh:$refreshSeconds;url=/");
    echo '<!DOCTYPE HTML>
<html lang="es">
<head>
    <title>' . $safeTitle . '</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
    <link rel="shortcut icon" href="favicon.png">
    <style>
        :root {
            color-scheme: light;
            --ink: #20313a;
            --muted: #65747b;
            --paper: rgba(255, 255, 255, 0.9);
            --line: rgba(32, 49, 58, 0.14);
            --accent: #2f766d;
            --accent-dark: #1f564f;
            --sand: #f4ead8;
            --sky: #dceff0;
        }

        * {
            box-sizing: border-box;
        }

        body {
            min-height: 100vh;
            margin: 0;
            display: grid;
            place-items: center;
            padding: 2rem;
            color: var(--ink);
            font-family: Arial, Helvetica, sans-serif;
            background:
                linear-gradient(145deg, rgba(220, 239, 240, 0.95), rgba(244, 234, 216, 0.85)),
                radial-gradient(circle at 20% 20%, rgba(47, 118, 109, 0.18), transparent 32%),
                radial-gradient(circle at 80% 78%, rgba(124, 91, 55, 0.14), transparent 30%);
        }

        .message-shell {
            width: min(760px, 100%);
            position: relative;
            padding: clamp(1.5rem, 5vw, 3rem);
        }

        .message-card {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--paper);
            box-shadow: 0 28px 80px rgba(32, 49, 58, 0.18);
        }

        .message-card::before {
            content: "";
            display: block;
            height: 8px;
            background: linear-gradient(90deg, var(--accent), #8a6b43, var(--accent-dark));
        }

        .message-content {
            padding: clamp(2rem, 6vw, 4rem);
            text-align: center;
        }

        .message-mark {
            width: 72px;
            height: 72px;
            display: grid;
            place-items: center;
            margin: 0 auto 1.35rem;
            border: 1px solid rgba(47, 118, 109, 0.25);
            border-radius: 50%;
            color: var(--accent-dark);
            background: rgba(47, 118, 109, 0.08);
            font-size: 2rem;
            line-height: 1;
        }

        h1 {
            max-width: 12em;
            margin: 0 auto;
            font-size: clamp(1.75rem, 5vw, 3.35rem);
            line-height: 1.08;
            font-weight: 700;
            letter-spacing: 0;
        }

        .progress {
            height: 4px;
            width: 100%;
            overflow: hidden;
            background: rgba(32, 49, 58, 0.1);
        }

        .progress span {
            display: block;
            height: 100%;
            width: 100%;
            background: var(--accent);
            transform-origin: left;
            animation: returnHome ' . (int)$refreshSeconds . 's linear forwards;
        }

        @keyframes returnHome {
            from {
                transform: scaleX(1);
            }
            to {
                transform: scaleX(0);
            }
        }

        @media (max-width: 520px) {
            body {
                padding: 1rem;
            }

            .message-content {
                padding: 2rem 1.25rem;
            }
        }
    </style>
</head>
<body>
    <main class="message-shell">
        <section class="message-card" aria-live="polite">
            <div class="message-content">
                <div class="message-mark" aria-hidden="true">' . $icon . '</div>
                ' . $message . '
            </div>
            <div class="progress" aria-hidden="true"><span></span></div>
        </section>
    </main>
</body>
</html>';
}

function send_response($title, $messageHtml, $variant = 'success', $statusCode = 200, $refreshSeconds = 5) {
    $isAjax = isset($_POST['ajax']);
    if ($isAjax) {
        http_response_code($statusCode);
        header('Content-Type: application/json; charset=UTF-8');
        echo json_encode([
            'success' => $variant === 'success',
            'message' => $title
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    http_response_code($statusCode);
    render_response_page($title, $messageHtml, $variant, $refreshSeconds);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    send_response(
        'Formulario no enviado',
        '<h1>Formulario no enviado.</h1>',
        'error',
        405,
        3
    );
}

$token = isset($_POST['csrf_token']) ? $_POST['csrf_token'] : '';
if (!verify_csrf_token($token)) {
    send_response(
        'Error de seguridad: Token de verificación inválido.',
        '<h1>Error de seguridad: Token de verificación inválido.</h1>',
        'error',
        403,
        3
    );
}

include_once('db.php');

// Trampa antispam: el campo "website" esta oculto con CSS, asi que una persona
// nunca lo rellena. Si viene con contenido es un bot; se le responde como si
// todo hubiera ido bien para no darle pistas de que ha sido detectado.
if (!empty($_POST['website'])) {
    send_response(
        'Mensaje enviado',
        '<h1>Gracias por tus pensamientos. Serán enviados a las estrellas.</h1>'
    );
}

// Limitador simple: como maximo 3 envios cada 10 minutos por sesion, para que
// un bot que haya superado la trampa no llene la tabla de mensajes.
$ahora = time();
$historial = (isset($_SESSION['contact_times']) && is_array($_SESSION['contact_times']))
    ? $_SESSION['contact_times']
    : [];
$historial = array_values(array_filter($historial, function ($marca) use ($ahora) {
    return ($ahora - $marca) < 600;
}));

if (count($historial) >= 3) {
    send_response(
        'Has enviado varios mensajes seguidos. Espera unos minutos antes de volver a escribir.',
        '<h1>Has enviado varios mensajes seguidos.</h1><p style="color:#65747b;line-height:1.7;margin-top:1rem;">Espera unos minutos antes de volver a escribir. Si es urgente, escríbeme directamente a tkplts@gmail.com.</p>',
        'error',
        429,
        5
    );
}

// OJO: el intento NO se registra todavia. Se registra solo cuando el mensaje
// entra en la base de datos, mas abajo. Antes se registraba aqui, y eso tenia
// un fallo real: como las validaciones (nombre corto, correo mal escrito...)
// devuelven 400 sin guardar nada, una persona que fallaba tres veces seguidas
// por escribir mal su correo se quedaba bloqueada 10 minutos SIN haber enviado
// nada. Con el registro solo en el exito, el tope de 3 cada 10 minutos sigue
// protegiendo la base de datos, pero los intentos fallidos no consumen cupo.

/**
 * Normaliza la entrada: recorta, quita caracteres de control y limita la
 * longitud. El escape HTML se hace en la SALIDA (send_response), no aqui.
 * El limite es configurable porque el mensaje admite 2000 caracteres y el
 * nombre solo 80: usar un unico tope de 500 recortaba los mensajes largos.
 */
function sanitize_input($data, $limit = 500) {
    $data = trim((string) $data);
    $data = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $data);
    return mb_substr($data, 0, $limit);
}

$visitor_name = isset($_POST['visitor_name']) ? sanitize_input($_POST['visitor_name'], 80) : '';
$visitor_email = isset($_POST['visitor_email']) ? sanitize_input($_POST['visitor_email'], 120) : '';
$visitor_message = isset($_POST['visitor_message']) ? sanitize_input($_POST['visitor_message'], 2000) : '';
$email_title = isset($_POST['email_title']) ? sanitize_input($_POST['email_title'], 120) : '';

$errors = [];
if ($visitor_name === '' || mb_strlen($visitor_name) < 2) {
    $errors[] = 'El nombre es obligatorio (mínimo 2 caracteres)';
}
if ($visitor_email === '') {
    $errors[] = 'El correo es obligatorio';
} elseif (!filter_var($visitor_email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'El correo no es válido';
}
if (mb_strlen($email_title) < 3) {
    $errors[] = 'El asunto es obligatorio (mínimo 3 caracteres)';
}
if (mb_strlen($visitor_message) < 10) {
    $errors[] = 'El mensaje es obligatorio (mínimo 10 caracteres)';
}

if (!empty($errors)) {
    $items = '';
    foreach ($errors as $error) {
        $items .= '<li>' . htmlspecialchars($error, ENT_QUOTES, 'UTF-8') . '</li>';
    }

    send_response(
        'Revisa el formulario: ' . implode('. ', $errors) . '.',
        '<h1>Por favor, corrige los siguientes errores:</h1><ul style="margin:1.5rem auto 0; max-width:28rem; text-align:left; color:#65747b; line-height:1.7;">' . $items . '</ul>',
        'error',
        400
    );
}

$visita = $visitor_name;
date_default_timezone_set("Europe/Madrid");
$fecha = date('Y-m-d H:i:s');

$visita = $visitor_name;
date_default_timezone_set("Europe/Madrid");
$fecha = date('Y-m-d H:i:s');

// Guarda por si db.php no llego a conectar (servidor de la base de datos caido,
// credenciales cambiadas...). Sin esto, mysqli_prepare(null) mata el script con
// un fatal en vez de dar el mensaje de error educado.
if (!isset($conectar) || $conectar === false || $conectar instanceof mysqli === false) {
    send_response(
        'Servicio de mensajes no disponible',
        '<h1>El buzón no está disponible en este momento.</h1><p style="color:#65747b;line-height:1.7;margin-top:1rem;">Inténtalo de nuevo en unos minutos o escríbeme directamente a tkplts@gmail.com.</p>',
        'error',
        500
    );
}

$stmt = mysqli_prepare($conectar, "INSERT INTO `mensajes` (`id`, `visitor_name`, `visitor_email`, `visitor_message`, `email_title`, `fecha`) VALUES (NULL, ?, ?, ?, ?, ?)");
if (!$stmt) {
    send_response(
        'Error al preparar el mensaje',
        '<h1>Ha ocurrido un error al preparar tu mensaje. Por favor, inténtalo de nuevo más tarde.</h1>',
        'error',
        500
    );
}

mysqli_stmt_bind_param($stmt, "sssss", $visitor_name, $visitor_email, $visitor_message, $email_title, $fecha);

if (mysqli_stmt_execute($stmt)) {
    mysqli_stmt_close($stmt);
    mysqli_close($conectar);
    // Envio real: ahora si consume cupo del limitador (ver la nota de arriba)
    $historial[] = $ahora;
    $_SESSION['contact_times'] = $historial;
    send_response(
        'Mensaje enviado',
        "<h1>Gracias por tus pensamientos, " . htmlspecialchars($visita, ENT_QUOTES, 'UTF-8') . ". Serán enviados a las estrellas, ellas sabrán darte una respuesta.</h1>"
    );
} else {
    mysqli_stmt_close($stmt);
    mysqli_close($conectar);
    send_response(
        'Error al enviar el mensaje',
        '<h1>Ha ocurrido un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.</h1>',
        'error',
        500
    );
}
?>
