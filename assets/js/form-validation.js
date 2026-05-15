/**
 * Validación del formulario de contacto
 * Este script proporciona validación adicional del lado del cliente
 * para el formulario de contacto en la página principal.
 */

document.addEventListener('DOMContentLoaded', function () {
    const contactForm = document.querySelector('form[action="contact.php"]');

    if (contactForm) {
        fetch('get_token.php')
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                const tokenInput = document.getElementById('csrf_token');
                if (tokenInput && data.csrf_token) {
                    tokenInput.value = data.csrf_token;
                }
            })
            .catch(function () {
                console.log('No se pudo cargar el token de seguridad del formulario.');
            });

        // Validar el formulario antes de enviarlo
        contactForm.addEventListener('submit', function (event) {
            let isValid = true;
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const titleInput = document.getElementById('title1');
            const messageInput = document.getElementById('message');

            // Validar nombre (solo letras y espacios)
            if (nameInput && nameInput.value) {
                const namePattern = /^[a-zA-ZÀ-ÿ\u00f1\u00d1]+(\s*[a-zA-ZÀ-ÿ\u00f1\u00d1]*)*[a-zA-ZÀ-ÿ\u00f1\u00d1]+$/;
                if (!namePattern.test(nameInput.value.trim())) {
                    isValid = false;
                    nameInput.classList.add('error');
                } else {
                    nameInput.classList.remove('error');
                }
            }

            // Validar email
            if (emailInput && emailInput.value) {
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailPattern.test(emailInput.value.trim())) {
                    isValid = false;
                    emailInput.classList.add('error');
                } else {
                    emailInput.classList.remove('error');
                }
            }

            // Validar título
            if (titleInput && !titleInput.value.trim()) {
                isValid = false;
                titleInput.classList.add('error');
            } else if (titleInput) {
                titleInput.classList.remove('error');
            }

            // Validar mensaje
            if (messageInput && !messageInput.value.trim()) {
                isValid = false;
                messageInput.classList.add('error');
            } else if (messageInput) {
                messageInput.classList.remove('error');
            }

            if (!isValid) {
                event.preventDefault();
                alert('Por favor, completa correctamente todos los campos requeridos.');
            }
        });
    }
});
