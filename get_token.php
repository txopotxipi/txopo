<?php
require_once 'csrf_utils.php';

$token = generate_csrf_token();

header('Content-Type: application/json; charset=UTF-8');
header('Cache-Control: no-store, max-age=0');
header('X-Content-Type-Options: nosniff');

echo json_encode([
    'token' => $token,
    'csrf_token' => $token
]);
?>
