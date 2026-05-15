<?php
require_once 'csrf_utils.php';

header('Content-Type: application/json; charset=UTF-8');
echo json_encode(['csrf_token' => generate_csrf_token()]);
?>
