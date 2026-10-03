<?php
/**
 * mensajes.php — Buzón privado de Txopo Txipi
 * ===========================================================================
 *
 * Página PRIVADA para leer los mensajes que la gente deja en el formulario de
 * contacto (tabla `mensajes` de la base de datos MySQL de InfinityFree).
 *
 * ESTE FICHERO NO CONTIENE NINGÚN SECRETO y puede estar en un repositorio
 * público sin riesgo: la contraseña del panel y las credenciales de la base de
 * datos viven fuera del repositorio (db.php / config/panel_config.php, ambos
 * en .gitignore y subidos a mano al servidor).
 *
 * Cómo se entra
 * -------------
 * Hay dos modos, por orden de preferencia:
 *
 *   1. RECOMENDADO — contraseña propia del panel. Se define una sola vez en
 *      db.php (o en config/panel_config.php) así:
 *
 *          $CLAVE_PANEL_HASH = '$2y$10$........................';
 *
 *      El valor se genera con password_hash('tu-contraseña', PASSWORD_DEFAULT)
 *      y NUNCA se escribe la contraseña en claro en ningún sitio.
 *
 *   2. PROVISIONAL — si no hay $CLAVE_PANEL_HASH, se entra con la propia
 *      contraseña de MySQL (la de db.php). Sirve para empezar a usarlo sin
 *      tocar nada, pero lo suyo es pasar al modo 1.
 *
 * Seguridad
 * ---------
 *  - Sesión propia y aislada (`txopo_panel`), con cookie HttpOnly + Secure +
 *    SameSite=Strict: no interfiere con la sesión del formulario de contacto.
 *  - La contraseña se compara en tiempo constante y, en el modo 1, contra un
 *    hash bcrypt (nunca contra texto en claro).
 *  - Bloqueo anti fuerza bruta: 6 fallos por IP en 15 minutos.
 *  - Token CSRF en todas las acciones que modifican datos.
 *  - Todas las consultas van con sentencias preparadas y toda la salida se
 *    escapa con htmlspecialchars.
 *  - noindex: la página no se indexa ni se enlaza desde el sitio.
 */

// ---------------------------------------------------------------------------
//  Sesión propia, aislada de la del formulario de contacto
// ---------------------------------------------------------------------------

session_name('txopo_panel');

// La cookie se marca "Secure" siempre que la peticion venga por HTTPS. En el
// servidor real (InfinityFree sirve el sitio por HTTPS) esto siempre es cierto;
// la deteccion existe solo para no romper las pruebas en local sobre HTTP.
$esHttps = (!empty($_SERVER['HTTPS']) && strtolower((string) $_SERVER['HTTPS']) !== 'off')
    || (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && strtolower((string) $_SERVER['HTTP_X_FORWARDED_PROTO']) === 'https')
    || (isset($_SERVER['SERVER_PORT']) && (int) $_SERVER['SERVER_PORT'] === 443);

if (PHP_VERSION_ID >= 70300) {
    session_set_cookie_params([
        'lifetime' => 0,
        'path'     => '/',
        'httponly' => true,
        'secure'   => $esHttps,
        'samesite' => 'Strict',
    ]);
} else {
    session_set_cookie_params(0, '/; samesite=Strict', '', $esHttps, true);
}

session_start();

header('X-Robots-Tag: noindex, nofollow, noarchive, nosnippet');
header('Referrer-Policy: no-referrer');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store, no-cache, must-revalidate');

// ---------------------------------------------------------------------------
//  Base de datos (db.php está en el servidor y NO en el repositorio)
// ---------------------------------------------------------------------------

$rutaDb = __DIR__ . '/db.php';
if (!is_file($rutaDb)) {
    http_response_code(500);
    header('Content-Type: text/plain; charset=utf-8');
    exit('Falta el fichero de configuración de la base de datos (db.php).');
}
require_once $rutaDb;   // deja listo $conectar

// ---------------------------------------------------------------------------
//  Configuración de la contraseña del panel
// ---------------------------------------------------------------------------

$CLAVE_PANEL_HASH = null;

if (file_exists(__DIR__ . '/config/panel_config.php')) {
    include_once __DIR__ . '/config/panel_config.php';
}
if (isset($CLAVE_PANEL_HASH) && is_string($CLAVE_PANEL_HASH) && $CLAVE_PANEL_HASH !== '') {
    $modoClave = 'panel';
} else {
    $CLAVE_PANEL_HASH = null;
    $modoClave = 'mysql';   // provisional: se usa la contraseña de MySQL
}

/** Comprueba la contraseña en tiempo constante. */
function clave_correcta($introducida)
{
    global $CLAVE_PANEL_HASH, $passworddb;

    // Una contraseña vacía nunca vale, aunque la configurada lo estuviera.
    if (!is_string($introducida) || $introducida === '') {
        return false;
    }

    if ($CLAVE_PANEL_HASH !== null) {
        return password_verify($introducida, $CLAVE_PANEL_HASH);
    }

    // Modo provisional: la contraseña de MySQL, comparada sin filtrar tiempos.
    return isset($passworddb) && is_string($passworddb) && $passworddb !== ''
        && hash_equals($passworddb, $introducida);
}

// ---------------------------------------------------------------------------
//  Bloqueo anti fuerza bruta (6 fallos por IP cada 15 minutos)
// ---------------------------------------------------------------------------

const MAX_FALLOS   = 6;
const VENTANA      = 900;   // 15 minutos
const FICHERO_INTENTOS = 'config/panel_intentos.json';

/** Ruta del fichero de intentos; null si no se puede escribir. */
function ruta_intentos()
{
    $dir = __DIR__ . '/config';
    if (!is_dir($dir)) {
        @mkdir($dir, 0755, true);
    }
    if (!is_dir($dir) || !is_writable($dir)) {
        return null;
    }
    return __DIR__ . '/' . FICHERO_INTENTOS;
}

function leer_intentos()
{
    $ruta = ruta_intentos();
    if ($ruta === null || !file_exists($ruta)) {
        return [];
    }
    $datos = json_decode((string) @file_get_contents($ruta), true);
    return is_array($datos) ? $datos : [];
}

function guardar_intentos(array $datos)
{
    $ruta = ruta_intentos();
    if ($ruta === null) {
        return;
    }
    @file_put_contents($ruta, json_encode($datos), LOCK_EX);
}

function clave_ip()
{
    $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'desconocida';
    return substr(hash('sha256', 'txopo-panel:' . $ip), 0, 32);
}

/** Fallos recientes de esta IP. */
function fallos_recientes()
{
    $datos = leer_intentos();
    $clave = clave_ip();
    $ahora = time();
    $lista = isset($datos[$clave]) ? $datos[$clave] : [];
    $lista = array_values(array_filter($lista, function ($t) use ($ahora) {
        return is_int($t) && ($ahora - $t) < VENTANA;
    }));
    $datos[$clave] = $lista;
    guardar_intentos($datos);
    return $lista;
}

function anotar_fallo()
{
    $datos = leer_intentos();
    $clave = clave_ip();
    $lista = isset($datos[$clave]) ? $datos[$clave] : [];
    $lista[] = time();
    $datos[$clave] = array_slice($lista, -30);
    // Limpieza de entradas viejas para que el fichero no crezca.
    $ahora = time();
    foreach ($datos as $k => $v) {
        if (!is_array($v)) { unset($datos[$k]); continue; }
        $vivas = array_values(array_filter($v, function ($t) use ($ahora) {
            return is_int($t) && ($ahora - $t) < VENTANA;
        }));
        if (empty($vivas)) { unset($datos[$k]); } else { $datos[$k] = $vivas; }
    }
    guardar_intentos($datos);
}

function limpiar_fallos()
{
    $datos = leer_intentos();
    unset($datos[clave_ip()]);
    guardar_intentos($datos);
}

// ---------------------------------------------------------------------------
//  Token CSRF propio del panel
// ---------------------------------------------------------------------------

if (empty($_SESSION['panel_csrf'])) {
    $_SESSION['panel_csrf'] = bin2hex(random_bytes(32));
}
$csrf = $_SESSION['panel_csrf'];

function csrf_ok($recibido)
{
    global $csrf;
    return is_string($recibido) && $recibido !== '' && hash_equals($csrf, $recibido);
}

// ---------------------------------------------------------------------------
//  Estado de la sesión
// ---------------------------------------------------------------------------

$autenticado = !empty($_SESSION['panel_ok']);
$aviso       = '';
$tipoAviso   = 'error';

// ---------------------------------------------------------------------------
//  Cerrar sesión
// ---------------------------------------------------------------------------

if (isset($_GET['salir'])) {
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000, $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();
    header('Location: mensajes.php');
    exit;
}

// ---------------------------------------------------------------------------
//  Entrar
// ---------------------------------------------------------------------------

if (!$autenticado && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['accion']) && $_POST['accion'] === 'entrar') {

    $fallos = fallos_recientes();

    if (count($fallos) >= MAX_FALLOS) {
        $espera = VENTANA - (time() - min($fallos));
        $minutos = max(1, (int) ceil($espera / 60));
        $aviso = 'Demasiados intentos fallidos. Vuelve a probar dentro de ' . $minutos . ' minuto' . ($minutos === 1 ? '' : 's') . '.';
    } elseif (clave_correcta(isset($_POST['clave']) ? $_POST['clave'] : '')) {
        limpiar_fallos();
        session_regenerate_id(true);
        $_SESSION['panel_ok']  = true;
        $_SESSION['panel_cuando'] = time();
        $autenticado = true;
        header('Location: mensajes.php');
        exit;
    } else {
        anotar_fallo();
        $aviso = 'Contraseña incorrecta.';
    }
}

// ---------------------------------------------------------------------------
//  Acciones sobre los mensajes (solo con sesión y token válidos)
// ---------------------------------------------------------------------------

$tieneLeido = false;
$res = mysqli_query($conectar, "SHOW COLUMNS FROM `mensajes` LIKE 'leido'");
if ($res && mysqli_num_rows($res) > 0) {
    $tieneLeido = true;
}

if ($autenticado && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['accion']) && $_POST['accion'] !== 'entrar') {

    if (!csrf_ok(isset($_POST['csrf']) ? $_POST['csrf'] : '')) {
        $aviso = 'La sesión ha caducado. Vuelve a intentarlo.';
    } else {
        $accion = (string) $_POST['accion'];
        $id     = isset($_POST['id']) ? (int) $_POST['id'] : 0;

        if ($accion === 'preparar') {
            if ($tieneLeido) {
                $aviso = 'La base de datos ya estaba preparada.';
                $tipoAviso = 'ok';
            } elseif (mysqli_query($conectar, "ALTER TABLE `mensajes` ADD COLUMN `leido` TINYINT(1) NOT NULL DEFAULT 0")) {
                $tieneLeido = true;
                $aviso = 'Listo: ya puedes marcar los mensajes como leídos.';
                $tipoAviso = 'ok';
            } else {
                $aviso = 'No se ha podido preparar la base de datos.';
            }
        } elseif ($accion === 'marcar_todo' && $tieneLeido) {
            mysqli_query($conectar, "UPDATE `mensajes` SET `leido` = 1 WHERE `leido` = 0");
            $aviso = 'Todos los mensajes quedan marcados como leídos.';
            $tipoAviso = 'ok';
        } elseif ($id > 0 && in_array($accion, ['leer', 'no_leer', 'borrar'], true)) {
            if ($accion === 'borrar') {
                $stmt = mysqli_prepare($conectar, "DELETE FROM `mensajes` WHERE `id` = ?");
                mysqli_stmt_bind_param($stmt, 'i', $id);
                $ok = mysqli_stmt_execute($stmt);
                mysqli_stmt_close($stmt);
                $aviso = $ok ? 'Mensaje borrado.' : 'No se ha podido borrar el mensaje.';
                $tipoAviso = $ok ? 'ok' : 'error';
            } elseif ($tieneLeido) {
                $valor = $accion === 'leer' ? 1 : 0;
                $stmt = mysqli_prepare($conectar, "UPDATE `mensajes` SET `leido` = ? WHERE `id` = ?");
                mysqli_stmt_bind_param($stmt, 'ii', $valor, $id);
                $ok = mysqli_stmt_execute($stmt);
                mysqli_stmt_close($stmt);
                $aviso = $ok ? 'Mensaje actualizado.' : 'No se ha podido actualizar el mensaje.';
                $tipoAviso = $ok ? 'ok' : 'error';
            }
        } else {
            $aviso = 'Acción no reconocida.';
        }
    }
}

// ---------------------------------------------------------------------------
//  Leer los mensajes
// ---------------------------------------------------------------------------

$mensajes      = [];
$total         = 0;
$pagina        = isset($_GET['p']) ? max(1, (int) $_GET['p']) : 1;
$porPagina     = 20;
$busqueda      = isset($_GET['q']) ? trim((string) $_GET['q']) : '';
$totalPaginas  = 1;
$sinLeer       = 0;

if ($autenticado) {

    $where  = '';
    $tipos  = '';
    $params = [];

    if ($busqueda !== '') {
        $where = " WHERE (`visitor_name` LIKE ? OR `visitor_email` LIKE ? OR `email_title` LIKE ? OR `visitor_message` LIKE ?)";
        $comodin = '%' . str_replace(['%', '_'], ['\%', '\_'], $busqueda) . '%';
        $tipos  = 'ssss';
        $params = [$comodin, $comodin, $comodin, $comodin];
    }

    // Total
    $sqlTotal = "SELECT COUNT(*) AS n FROM `mensajes`" . $where;
    $stmt = mysqli_prepare($conectar, $sqlTotal);
    if ($stmt) {
        if ($tipos !== '') {
            mysqli_stmt_bind_param($stmt, $tipos, ...$params);
        }
        mysqli_stmt_execute($stmt);
        $r = mysqli_stmt_get_result($stmt);
        if ($r && ($fila = mysqli_fetch_assoc($r))) {
            $total = (int) $fila['n'];
        }
        mysqli_stmt_close($stmt);
    }

    $totalPaginas = max(1, (int) ceil($total / $porPagina));
    if ($pagina > $totalPaginas) {
        $pagina = $totalPaginas;
    }
    $desplazamiento = ($pagina - 1) * $porPagina;

    // Página actual
    $columnas = "`id`, `visitor_name`, `visitor_email`, `email_title`, `visitor_message`, `fecha`";
    if ($tieneLeido) {
        $columnas .= ", `leido`";
    }
    $sql = "SELECT " . $columnas . " FROM `mensajes`" . $where . " ORDER BY `id` DESC LIMIT ?, ?";
    $stmt = mysqli_prepare($conectar, $sql);
    if ($stmt) {
        if ($tipos !== '') {
            $tiposPag = $tipos . 'ii';
            $paramsPag = array_merge($params, [$desplazamiento, $porPagina]);
            mysqli_stmt_bind_param($stmt, $tiposPag, ...$paramsPag);
        } else {
            mysqli_stmt_bind_param($stmt, 'ii', $desplazamiento, $porPagina);
        }
        mysqli_stmt_execute($stmt);
        $r = mysqli_stmt_get_result($stmt);
        while ($r && ($fila = mysqli_fetch_assoc($r))) {
            $mensajes[] = $fila;
        }
        mysqli_stmt_close($stmt);
    }

    if ($tieneLeido) {
        $r = mysqli_query($conectar, "SELECT COUNT(*) AS n FROM `mensajes` WHERE `leido` = 0");
        if ($r && ($fila = mysqli_fetch_assoc($r))) {
            $sinLeer = (int) $fila['n'];
        }
    }
}

/** Escapa para HTML. */
function e($t)
{
    return htmlspecialchars((string) $t, ENT_QUOTES, 'UTF-8');
}

/** Fecha legible. */
function fecha_legible($f)
{
    $t = strtotime((string) $f);
    if (!$t) {
        return (string) $f;
    }
    $meses = ['', 'ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
    return date('j', $t) . ' ' . $meses[(int) date('n', $t)] . ' ' . date('Y', $t) . ' · ' . date('H:i', $t);
}

/** URL conservando la búsqueda. */
function url_pagina($p)
{
    $q = isset($_GET['q']) ? (string) $_GET['q'] : '';
    $u = 'mensajes.php?p=' . (int) $p;
    if ($q !== '') {
        $u .= '&q=' . urlencode($q);
    }
    return $u;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<title><?php echo $autenticado ? 'Mensajes recibidos' : 'Acceso privado'; ?> · Txopo Txipi</title>
<link rel="shortcut icon" href="favicon.png">
<style>
    :root {
        color-scheme: light;
        --ink: #20313a;
        --muted: #65747b;
        --line: rgba(32, 49, 58, 0.14);
        --paper: #ffffff;
        --fondo: #f4ead8;
        --accent: #2f766d;
        --accent-dark: #1f564f;
        --nuevo: #b45309;
    }
    * { box-sizing: border-box; }
    body {
        margin: 0;
        padding: 1.25rem;
        color: var(--ink);
        font-family: Arial, Helvetica, sans-serif;
        font-size: 16px;
        line-height: 1.55;
        background: linear-gradient(145deg, rgba(220, 239, 240, .95), rgba(244, 234, 216, .85));
        min-height: 100vh;
    }
    .marco { width: min(1100px, 100%); margin: 0 auto; }
    header.barra {
        display: flex; flex-wrap: wrap; gap: .75rem;
        align-items: baseline; justify-content: space-between;
        padding: 1rem 0 1.25rem;
    }
    header.barra h1 { margin: 0; font-size: 1.45rem; letter-spacing: -.01em; }
    header.barra .sub { color: var(--muted); font-size: .9rem; }
    .tarjeta {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: 0 18px 50px rgba(32, 49, 58, .10);
        overflow: hidden;
    }
    .entrar { max-width: 420px; margin: 8vh auto 0; padding: 2rem; }
    .entrar h1 { margin: 0 0 .35rem; font-size: 1.3rem; }
    .entrar p { margin: 0 0 1.25rem; color: var(--muted); font-size: .92rem; }
    label { display: block; font-size: .85rem; color: var(--muted); margin-bottom: .35rem; }
    input[type=password], input[type=search] {
        width: 100%; padding: .65rem .75rem; font-size: 1rem;
        border: 1px solid var(--line); border-radius: 6px;
        background: #fff; color: var(--ink);
    }
    input:focus-visible, button:focus-visible, a:focus-visible {
        outline: 3px solid rgba(47, 118, 109, .45); outline-offset: 2px;
    }
    button {
        font: inherit; cursor: pointer;
        border: 1px solid var(--line); border-radius: 6px;
        background: #fff; color: var(--ink);
        padding: .5rem .8rem;
    }
    button:hover { border-color: var(--accent); }
    a.boton {
        display: inline-block; text-decoration: none;
        font: inherit; cursor: pointer;
        border: 1px solid var(--line); border-radius: 6px;
        background: #fff; color: var(--ink);
        padding: .5rem .8rem;
    }
    a.boton:hover { border-color: var(--accent); }
    button.principal {
        width: 100%; margin-top: 1rem; padding: .7rem 1rem;
        background: var(--accent); border-color: var(--accent);
        color: #fff; font-weight: 700;
    }
    button.principal:hover { background: var(--accent-dark); border-color: var(--accent-dark); }
    button.peligro { color: #a11; }
    .aviso {
        padding: .7rem .9rem; border-radius: 6px; margin-bottom: 1rem;
        font-size: .92rem; border: 1px solid;
    }
    .aviso.error { background: #fdf2f2; border-color: #f3c4c4; color: #8a1c1c; }
    .aviso.ok    { background: #f1f8f4; border-color: #bfe0cd; color: #1c5b3a; }
    .barra-herramientas {
        display: flex; flex-wrap: wrap; gap: .6rem; align-items: center;
        padding: 1rem 1.25rem; border-bottom: 1px solid var(--line);
        background: #fbfaf7;
    }
    .barra-herramientas form { display: flex; gap: .5rem; flex: 1 1 260px; margin: 0; }
    .barra-herramientas input[type=search] { flex: 1 1 auto; }
    .contador { color: var(--muted); font-size: .88rem; }
    .contador b { color: var(--nuevo); }
    ul.lista { list-style: none; margin: 0; padding: 0; }
    ul.lista > li { border-bottom: 1px solid var(--line); padding: 1.1rem 1.25rem; }
    ul.lista > li:last-child { border-bottom: 0; }
    ul.lista > li.noleido { background: #fffdf7; }
    .cabecera-msg { display: flex; flex-wrap: wrap; gap: .5rem .9rem; align-items: baseline; justify-content: space-between; }
    .quien { font-weight: 700; }
    .correo { color: var(--muted); font-size: .88rem; }
    .cuando { color: var(--muted); font-size: .82rem; white-space: nowrap; }
    .etiqueta {
        display: inline-block; font-size: .72rem; font-weight: 700; letter-spacing: .04em;
        text-transform: uppercase; padding: .1rem .45rem; border-radius: 999px;
        background: #fdf0dc; color: var(--nuevo); border: 1px solid #f0d5a8;
    }
    .asunto { margin: .55rem 0 .35rem; font-weight: 700; }
    .cuerpo { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
    .acciones { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .8rem; }
    .acciones form { margin: 0; }
    .paginacion { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; justify-content: center; padding: 1rem; }
    .paginacion a, .paginacion span {
        padding: .4rem .7rem; border-radius: 6px; border: 1px solid var(--line);
        text-decoration: none; color: var(--ink); background: #fff;
    }
    .paginacion span.actual { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 700; }
    .vacio { padding: 2.5rem 1.25rem; text-align: center; color: var(--muted); }
    .pie { color: var(--muted); font-size: .82rem; text-align: center; padding: 1.25rem 0 2rem; }
    .pie a { color: var(--muted); }
    @media (max-width: 560px) {
        body { padding: .75rem; }
        .entrar { margin-top: 3vh; padding: 1.5rem; }
        ul.lista > li { padding: .9rem; }
    }
</style>
</head>
<body>
<div class="marco">

<?php if (!$autenticado): ?>

    <div class="tarjeta entrar">
        <h1>Acceso privado</h1>
        <p>Este es el buzón de mensajes de Txopo Txipi. Solo para el propietario del sitio.</p>

        <?php if ($aviso !== ''): ?>
            <div class="aviso error"><?php echo e($aviso); ?></div>
        <?php endif; ?>

        <form method="post" action="mensajes.php" autocomplete="off">
            <input type="hidden" name="accion" value="entrar">
            <label for="clave">Contraseña</label>
            <input type="password" id="clave" name="clave" required autofocus autocomplete="current-password">
            <button type="submit" class="principal">Entrar</button>
        </form>
    </div>

<?php else: ?>

    <header class="barra">
        <div>
            <h1>Mensajes recibidos</h1>
            <div class="sub">
                <?php echo (int) $total; ?> mensaje<?php echo $total === 1 ? '' : 's'; ?><?php
                if ($busqueda !== '') { echo ' para «' . e($busqueda) . '»'; }
                ?>
            </div>
        </div>
        <div>
            <a class="boton" href="mensajes.php?salir=1">Salir</a>
        </div>
    </header>

    <?php if ($aviso !== ''): ?>
        <div class="aviso <?php echo $tipoAviso === 'ok' ? 'ok' : 'error'; ?>"><?php echo e($aviso); ?></div>
    <?php endif; ?>

    <div class="tarjeta">

        <div class="barra-herramientas">
            <form method="get" action="mensajes.php">
                <input type="search" name="q" value="<?php echo e($busqueda); ?>" placeholder="Buscar por nombre, correo, asunto o texto…" aria-label="Buscar mensajes">
                <button type="submit">Buscar</button>
            </form>

            <?php if ($busqueda !== ''): ?>
                <a class="boton" href="mensajes.php">Ver todos</a>
            <?php endif; ?>

            <?php if ($tieneLeido): ?>
                <span class="contador">Sin leer: <b><?php echo (int) $sinLeer; ?></b></span>
                <?php if ($sinLeer > 0): ?>
                    <form method="post" action="mensajes.php">
                        <input type="hidden" name="csrf" value="<?php echo e($csrf); ?>">
                        <input type="hidden" name="accion" value="marcar_todo">
                        <button type="submit">Marcar todo como leído</button>
                    </form>
                <?php endif; ?>
            <?php else: ?>
                <form method="post" action="mensajes.php">
                    <input type="hidden" name="csrf" value="<?php echo e($csrf); ?>">
                    <input type="hidden" name="accion" value="preparar">
                    <button type="submit">Preparar (marcar leído/no leído)</button>
                </form>
            <?php endif; ?>
        </div>

        <?php if (empty($mensajes)): ?>
            <div class="vacio">
                <?php if ($busqueda !== ''): ?>
                    No hay ningún mensaje que coincida con «<?php echo e($busqueda); ?>».
                <?php else: ?>
                    Todavía no ha llegado ningún mensaje.
                <?php endif; ?>
            </div>
        <?php else: ?>
            <ul class="lista">
                <?php foreach ($mensajes as $m): ?>
                    <?php $nuevo = $tieneLeido && empty($m['leido']); ?>
                    <li class="<?php echo $nuevo ? 'noleido' : ''; ?>">
                        <div class="cabecera-msg">
                            <div>
                                <span class="quien"><?php echo e($m['visitor_name'] !== '' ? $m['visitor_name'] : '(sin nombre)'); ?></span>
                                <?php if (!empty($m['visitor_email'])): ?>
                                    <span class="correo">&lt;<?php echo e($m['visitor_email']); ?>&gt;</span>
                                <?php endif; ?>
                                <?php if ($nuevo): ?>
                                    <span class="etiqueta">Nuevo</span>
                                <?php endif; ?>
                            </div>
                            <span class="cuando"><?php echo e(fecha_legible($m['fecha'])); ?></span>
                        </div>

                        <p class="asunto"><?php echo e($m['email_title'] !== '' ? $m['email_title'] : '(sin asunto)'); ?></p>
                        <p class="cuerpo"><?php echo e($m['visitor_message']); ?></p>

                        <div class="acciones">
                            <?php if (!empty($m['visitor_email'])): ?>
                                <a class="boton" href="mailto:<?php echo e($m['visitor_email']); ?>?subject=<?php echo e(rawurlencode('Re: ' . $m['email_title'])); ?>">Responder</a>
                            <?php endif; ?>

                            <?php if ($tieneLeido): ?>
                                <form method="post" action="mensajes.php">
                                    <input type="hidden" name="csrf" value="<?php echo e($csrf); ?>">
                                    <input type="hidden" name="id" value="<?php echo (int) $m['id']; ?>">
                                    <input type="hidden" name="accion" value="<?php echo $nuevo ? 'leer' : 'no_leer'; ?>">
                                    <button type="submit"><?php echo $nuevo ? 'Marcar leído' : 'Marcar no leído'; ?></button>
                                </form>
                            <?php endif; ?>

                            <form method="post" action="mensajes.php" onsubmit="return confirm('¿Seguro que quieres borrar este mensaje? No se puede deshacer.');">
                                <input type="hidden" name="csrf" value="<?php echo e($csrf); ?>">
                                <input type="hidden" name="id" value="<?php echo (int) $m['id']; ?>">
                                <input type="hidden" name="accion" value="borrar">
                                <button type="submit" class="peligro">Borrar</button>
                            </form>
                        </div>
                    </li>
                <?php endforeach; ?>
            </ul>

            <?php if ($totalPaginas > 1): ?>
                <div class="paginacion">
                    <?php if ($pagina > 1): ?>
                        <a href="<?php echo e(url_pagina($pagina - 1)); ?>">← Anteriores</a>
                    <?php endif; ?>
                    <span class="actual">Página <?php echo (int) $pagina; ?> de <?php echo (int) $totalPaginas; ?></span>
                    <?php if ($pagina < $totalPaginas): ?>
                        <a href="<?php echo e(url_pagina($pagina + 1)); ?>">Siguientes →</a>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
        <?php endif; ?>

    </div>

    <div class="pie">
        Buzón privado · <?php echo (int) $total; ?> mensaje<?php echo $total === 1 ? '' : 's'; ?> en total ·
        <a href="index.html">Volver a la web</a>
    </div>

<?php endif; ?>

</div>
</body>
</html>
