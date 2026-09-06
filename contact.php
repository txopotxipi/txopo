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

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    render_response_page(
        'Formulario no enviado',
        '<h1>Formulario no enviado.</h1>',
        'error',
        3
    );
    exit;
}

$token = isset($_POST['csrf_token']) ? $_POST['csrf_token'] : '';
if (!verify_csrf_token($token)) {
    http_response_code(403);
    render_response_page(
        'Error de seguridad',
        '<h1>Error de seguridad: Token de verificación inválido.</h1>',
        'error',
        3
    );
    exit;
}

include_once('db.php');

function sanitize_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    return htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
}

$visitor_name = isset($_POST['visitor_name']) ? sanitize_input($_POST['visitor_name']) : '';
$visitor_email = isset($_POST['visitor_email']) ? sanitize_input($_POST['visitor_email']) : '';
$visitor_message = isset($_POST['visitor_message']) ? sanitize_input($_POST['visitor_message']) : '';
$email_title = isset($_POST['email_title']) ? sanitize_input($_POST['email_title']) : '';

$errors = [];
if ($visitor_name === '') {
    $errors[] = 'El nombre es obligatorio';
}
if ($visitor_email !== '' && !filter_var($visitor_email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'El correo no es válido';
}
if ($email_title === '') {
    $errors[] = 'El asunto es obligatorio';
}
if ($visitor_message === '') {
    $errors[] = 'El mensaje es obligatorio';
}

if (!empty($errors)) {
    $items = '';
    foreach ($errors as $error) {
        $items .= '<li>' . htmlspecialchars($error, ENT_QUOTES, 'UTF-8') . '</li>';
    }

    render_response_page(
        'Revisa el formulario',
        '<h1>Por favor, corrige los siguientes errores:</h1><ul style="margin:1.5rem auto 0; max-width:28rem; text-align:left; color:#65747b; line-height:1.7;">' . $items . '</ul>',
        'error'
    );
    mysqli_close($conectar);
    exit;
}

$visita = $visitor_name;
date_default_timezone_set("Europe/Madrid");
$fecha = date('Y-m-d H:i:s');

$stmt = mysqli_prepare($conectar, "INSERT INTO `mensajes` (`id`, `visitor_name`, `visitor_email`, `visitor_message`, `email_title`, `fecha`) VALUES (NULL, ?, ?, ?, ?, ?)");
if (!$stmt) {
    render_response_page(
        'Error al preparar el mensaje',
        '<h1>Ha ocurrido un error al preparar tu mensaje. Por favor, inténtalo de nuevo más tarde.</h1>',
        'error'
    );
    mysqli_close($conectar);
    exit;
}

mysqli_stmt_bind_param($stmt, "sssss", $visitor_name, $visitor_email, $visitor_message, $email_title, $fecha);

if (mysqli_stmt_execute($stmt)) {
    render_response_page(
        'Mensaje enviado',
        "<h1>Gracias por tus pensamientos, $visita. Serán enviados a las estrellas, ellas sabrán darte una respuesta.</h1>"
    );
} else {
    render_response_page(
        'Error al enviar el mensaje',
        '<h1>Ha ocurrido un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.</h1>',
        'error'
    );
}

mysqli_stmt_close($stmt);
mysqli_close($conectar);
?>
