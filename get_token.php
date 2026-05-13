<?php
require_once 'csrf_utils.php';
header('Content-Type: application/json');
echo json_encode(['csrf_token' => generate_csrf_token()]);
?>
