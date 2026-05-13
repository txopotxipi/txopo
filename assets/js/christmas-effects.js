/*
 * EFECTOS NAVIDEÑOS - christmas-effects.js
 * 
 * CÓMO DESACTIVAR DESPUÉS DE NAVIDAD:
 * 1. Elimina la línea <link rel="stylesheet" href="assets/css/christmas-effects.css"> de index.html
 * 2. Elimina la línea <script src="assets/js/christmas-effects.js"></script> de index.html
 * 3. Opcionalmente, elimina este archivo, christmas-effects.css y assets/images/grinch.png
 */

(function () {
    'use strict';

    // Configuración - Ajusta estos valores según tus preferencias
    const CONFIG = {
        snowflakes: {
            enabled: true,
            count: 30,           // Número de copos
            symbols: ['❄', '❅', '❆', '✻', '✼', '❉']
        },
        grinch: {
            enabled: true,
            minInterval: 10000,   // Mínimo 10 segundos
            maxInterval: 30000,   // Máximo 30 segundos
            visibleTime: 5000,    // Visible durante 5 segundos
            imagePath: 'assets/images/grinch.png'
        },
        lights: {
            enabled: true
        }
    };

    // ===== COPOS DE NIEVE =====
    function createSnowflakes() {
        if (!CONFIG.snowflakes.enabled) return;

        const container = document.createElement('div');
        container.className = 'snowflakes-container';
        container.setAttribute('aria-hidden', 'true');

        for (let i = 0; i < CONFIG.snowflakes.count; i++) {
            const snowflake = document.createElement('span');
            snowflake.className = 'snowflake';
            snowflake.textContent = CONFIG.snowflakes.symbols[
                Math.floor(Math.random() * CONFIG.snowflakes.symbols.length)
            ];
            snowflake.style.left = Math.random() * 100 + '%';
            snowflake.style.animationDelay = Math.random() * 5 + 's';
            snowflake.style.opacity = Math.random() * 0.5 + 0.5;
            container.appendChild(snowflake);
        }

        document.body.appendChild(container);
    }

    // ===== GRINCH ASOMÁNDOSE =====
    function createGrinch() {
        if (!CONFIG.grinch.enabled) return;

        const container = document.createElement('div');
        container.className = 'grinch-container left'; // Empieza por la izquierda
        container.setAttribute('aria-hidden', 'true');

        const img = document.createElement('img');
        img.src = CONFIG.grinch.imagePath;
        img.alt = '';
        img.loading = 'lazy';

        container.appendChild(img);
        document.body.appendChild(container);

        // Variable para rastrear el lado actual
        let isLeftSide = true;

        // Función auxiliar para obtener entero aleatorio
        function getRandomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1)) + min;
        }

        function showGrinch() {
            // 1. Alternar lado (Izquierda <-> Derecha)
            isLeftSide = !isLeftSide;

            // Limpiar clases previas de posición/efecto
            container.classList.remove('left', 'right', 'shimmy');

            // Asignar y configurar nuevo lado
            if (isLeftSide) {
                container.classList.add('left');
            } else {
                container.classList.add('right');
            }

            // 2. Altura Aleatoria (bottom)
            // Entre 0px (abajo del todo) y 60% de la altura de la pantalla
            // Evitamos que salga muy arriba para no tapar el menú si es sticky
            const randomBottom = getRandomInt(0, 60);
            container.style.bottom = randomBottom + '%';

            // 3. Efecto "Shimmy" (Baile vertical) aleatorio
            // 30% de probabilidad de que ocurra
            if (Math.random() < 0.3) {
                container.classList.add('shimmy');
            }

            // Mostrar el Grinch
            // Pequeño delay para permitir que el navegador aplique los cambios de posición antes de animar `left`/`right`
            requestAnimationFrame(() => {
                container.classList.add('visible');
            });

            // Ocultar después del tiempo visible
            setTimeout(function () {
                container.classList.remove('visible');

                // Programar la SIGUIENTE aparición con tiempo aleatorio
                scheduleNextGrinch();
            }, CONFIG.grinch.visibleTime);
        }

        function scheduleNextGrinch() {
            const nextTime = getRandomInt(CONFIG.grinch.minInterval, CONFIG.grinch.maxInterval);
            console.log(`🎅 El Grinch volverá en ${nextTime / 1000} segundos.`);
            setTimeout(showGrinch, nextTime);
        }

        // Iniciar el ciclo
        // Primera aparición un poco más rápida para testing/demo
        setTimeout(showGrinch, 3000);
    }

    // ===== LUCES NAVIDEÑAS COLGANTES =====
    function createChristmasLights() {
        if (!CONFIG.lights.enabled) return;

        const lights = document.createElement('div');
        lights.className = 'christmas-lights';
        lights.setAttribute('aria-hidden', 'true');

        // Colores de las bombillas
        const colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange'];
        const bulbCount = 25; // Número de bombillas

        for (let i = 0; i < bulbCount; i++) {
            const bulb = document.createElement('div');
            bulb.className = 'bulb ' + colors[i % colors.length];
            lights.appendChild(bulb);
        }

        document.body.appendChild(lights);
    }

    // ===== INICIALIZACIÓN =====
    // NIEVE: Ejecutar inmediatamente (prioridad máxima)
    // Insertamos directamente en document.body o documentElement si body no existe aún
    (function initSnowNow() {
        if (document.body) {
            createSnowflakes();
        } else {
            // Si body no existe, esperamos el mínimo necesario
            document.addEventListener('DOMContentLoaded', createSnowflakes);
        }
    })();

    // Grinch y luces: pueden esperar al DOM completo
    function initOtherEffects() {
        createGrinch();
        createChristmasLights();
        console.log('🎅 ¡Feliz Navidad! Efectos cargados.');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOtherEffects);
    } else {
        initOtherEffects();
    }

})();
