<?php
/**
 * Utilidad básica para la protección CSRF
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

/**
 * Genera un token CSRF y lo guarda en la sesión
 */
function generate_csrf_token() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

/**
 * Verifica si el token proporcionado coincide con el de la sesión
 */
function verify_csrf_token($token) {
    if (isset($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token)) {
        return true;
    }
    return false;
}
?>
