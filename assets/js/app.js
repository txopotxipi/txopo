(function () {
    const rawData = window.txopoSiteData || { featuredDestinations: [], journeys: [] };
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const finePointer = window.matchMedia("(pointer: fine)").matches;
    const EXPAND_STEP = 30;

    const state = {
        query: "",
        filter: "all",
        visible: EXPAND_STEP
    };

    const typeLabels = {
        all: "Todo",
        rutas: "Rutas",
        ciudades: "Ciudades",
        fiestas: "Fiestas",
        especiales: "Especiales",
        exterior: "Exterior"
    };

    const typeIcons = {
        rutas: "fa-mountain",
        ciudades: "fa-city",
        fiestas: "fa-music",
        especiales: "fa-compass",
        exterior: "fa-globe-europe"
    };

    function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, function (character) {
            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                "\"": "&quot;",
                "'": "&#39;"
            }[character];
        });
    }

    /* Los datos de sites-data.js pueden venir con "mojibake" (UTF-8 leido como
       Latin-1: "Ã±" en lugar de "ñ"). Aqui se reconstruyen los bytes originales
       y se vuelven a decodificar como UTF-8.
       Antes se hacia con escape()/decodeURIComponent(), pero escape() esta
       obsoleto y no existe en todos los entornos. */
    const utf8Decoder = (function () {
        try {
            return new TextDecoder("utf-8", { fatal: true });
        } catch (error) {
            return null;
        }
    })();

    function repairMojibake(value) {
        if (typeof value !== "string") {
            return value;
        }

        if (!utf8Decoder || !/[\u00c2\u00c3\u00c4]/.test(value)) {
            return value;
        }

        const bytes = new Uint8Array(value.length);
        for (let index = 0; index < value.length; index += 1) {
            bytes[index] = value.charCodeAt(index) & 0xff;
        }

        try {
            return utf8Decoder.decode(bytes);
        } catch (error) {
            /* Secuencia invalida: no era mojibake, se deja el texto original. */
            return value;
        }
    }

    function normalizeForSearch(value) {
        return repairMojibake(String(value || ""))
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .replace(/[^a-z0-9\s]/g, " ")
            .replace(/\s+/g, " ")
            .trim();
    }

    function normalizeHref(value) {
        return repairMojibake(String(value || ""))
            .replace(/\\+/g, "/")
            .replace(/\s+/g, " ")
            .trim();
    }

    function getJourneyType(entry) {
        const haystack = normalizeForSearch(entry.title + " " + entry.href);

        if (/(navidad|semana santa|orgullo|jaiak|hispanidad|athletic|champions|real madrid|verbena|portu jaiak|mexillonada|sabucedo|sanisidro|san patricio|dakidarria|ramoncin|marta|coro|mili|festa)/.test(haystack)) {
            return "fiestas";
        }

        if (/(praga|karlovy|florencia|ferrara|venecia|ravena|laponia|cesky|olivenza|evora|toledo|talavera|burgos|buitrago|yecla|alentejo|frias|ona|orbaneja|covarrubias|silos|palacio|laredo|poza|juan sebastian|puerto viejo|kotor|dubrovnik|split|zadar|budva|mostar|trogir|zagreb)/.test(haystack)) {
            return "ciudades";
        }

        if (/(amboto|gorbea|pagasarri|panticosa|oroel|ibon|estan|cascadas|fervenzas|faro|desfiladero|sonabia|ason|gorliz|serantes|puron|cazadores|cahorros|monachil|alpujarra|aguino|torla|gollizno|ebro|tobalina|tobera|puentedey|aljibe|caballo|mea|santiaguino|plitvice)/.test(haystack)) {
            return "rutas";
        }

        if (entry.external) {
            return "exterior";
        }

        return "especiales";
    }

    function normalizeJourney(entry) {
        const title = repairMojibake(entry.title);
        const href = normalizeHref(entry.href);
        const external = /^https?:/i.test(href);
        const type = getJourneyType({ title, href, external });

        return {
            title,
            href,
            external,
            type,
            searchIndex: normalizeForSearch([title, href, typeLabels[type], external ? "exterior externo" : ""].join(" ")),
            safeHref: external ? href : encodeURI(href)
        };
    }

    function normalizeFeature(entry) {
        return {
            title: repairMojibake(entry.title),
            href: normalizeHref(entry.href),
            image: normalizeHref(entry.image),
            /* Version WebP de la miniatura (opcional). Si existe, la tarjeta
               se pinta con <picture> y el navegador elige el WebP; si no,
               cae al .jpg normal. Se generan con generar_thumbs.py. */
            imageWebp: normalizeHref(entry.imageWebp || ""),
            tag: repairMojibake(entry.tag),
            description: repairMojibake(entry.description),
            safeHref: encodeURI(normalizeHref(entry.href)),
            safeImage: encodeURI(normalizeHref(entry.image)),
            safeImageWebp: entry.imageWebp ? encodeURI(normalizeHref(entry.imageWebp)) : ""
        };
    }

    const featuredDestinations = rawData.featuredDestinations.map(normalizeFeature);
    const journeys = rawData.journeys
        .map(normalizeJourney)
        .sort(function (left, right) {
            return left.title.localeCompare(right.title, "es", { sensitivity: "base" });
        });

    function renderFeatured() {
        const featuredGrid = document.getElementById("featuredGrid");
        if (!featuredGrid) {
            return;
        }

        featuredGrid.innerHTML = featuredDestinations.map(function (item, index) {
            /* La imagen va en un <picture> cuando hay version WebP: los
               navegadores que entienden WebP (practicamente todos) bajan la
               miniatura ligera y el resto usa el .jpg de respaldo. Sin este
               envoltorio no habria forma de ofrecer WebP con garantia de
               respaldo en una etiqueta <img> normal. */
            const mediaHtml = item.safeImageWebp
                ? '<picture>' +
                  '<source type="image/webp" srcset="' + escapeHtml(item.safeImageWebp) + '">' +
                  '<img src="' + escapeHtml(item.safeImage) + '" alt="Fotografia de ' + escapeHtml(item.title) + '" loading="lazy" decoding="async">' +
                  '</picture>'
                : '<img src="' + escapeHtml(item.safeImage) + '" alt="Fotografia de ' + escapeHtml(item.title) + '" loading="lazy" decoding="async">';

            return [
                '<a class="featured-card" href="' + escapeHtml(item.safeHref) + '" target="_blank" rel="noopener" style="--card-delay:' + (index * 110) + 'ms">',
                '  <span class="featured-media">',
                '    ' + mediaHtml,
                "  </span>",
                '  <span class="featured-content">',
                '    <span class="featured-meta">' + escapeHtml(item.tag) + "</span>",
                "    <h3>" + escapeHtml(item.title) + "</h3>",
                "    <p>" + escapeHtml(item.description) + "</p>",
                '    <span class="featured-link">Abrir viaje</span>',
                "  </span>",
                "</a>"
            ].join("");
        }).join("");
    }

    function createJourneyCard(item) {
        const iconClass = typeIcons[item.type] || typeIcons.especiales;
        const externalBadge = item.external
            ? '<span class="external-badge">Externo</span>'
            : "";

        return [
            '<a class="journey-card' + (item.external ? " is-external" : "") + '" href="' + escapeHtml(item.safeHref) + '" target="_blank" rel="noopener">',
            '  <span class="journey-card-shine"></span>',
            '  <span class="journey-icon"><i class="icon solid ' + iconClass + '" aria-hidden="true"></i></span>',
            '  <span class="journey-body">',
            "    <strong>" + escapeHtml(item.title) + "</strong>",
            "    <span>" + escapeHtml(typeLabels[item.type]) + "</span>",
            externalBadge,
            "  </span>",
            '  <span class="journey-arrow">Abrir</span>',
            "</a>"
        ].join("");
    }

    function updateSummary(filtered) {
        const resultsSummary = document.getElementById("resultsSummary");
        if (!resultsSummary) {
            return;
        }

        const hidden = filtered.length - state.visible;
        const hasMore = hidden > 0;

        if (!filtered.length) {
            resultsSummary.textContent = "No hay coincidencias con el filtro actual. Prueba otro nombre o abre de nuevo el mapa completo.";
            return;
        }

        if (filtered.length === journeys.length && !hasMore) {
            resultsSummary.textContent = journeys.length + " destinos listos para abrir.";
            return;
        }

        resultsSummary.textContent = filtered.length + " resultados de " + journeys.length + (hasMore ? " · mostrando " + state.visible + " (" + hidden + " más)" : "");
    }

    function renderJourneys() {
        const journeyGrid = document.getElementById("journeyGrid");
        if (!journeyGrid) {
            return;
        }

        const query = normalizeForSearch(state.query);
        const filtered = journeys.filter(function (item) {
            const matchesFilter = state.filter === "all" || item.type === state.filter || (state.filter === "exterior" && item.external);
            const matchesQuery = !query || item.searchIndex.indexOf(query) !== -1;
            return matchesFilter && matchesQuery;
        });

        updateSummary(filtered);

        if (!filtered.length) {
            journeyGrid.innerHTML = '<div class="empty-state">No aparece ningun viaje con ese criterio. Borra parte de la busqueda o cambia el filtro para volver a ver el archivo completo.</div>';
            updateLoadMore(0);
            return;
        }

        journeyGrid.innerHTML = filtered.slice(0, state.visible).map(createJourneyCard).join("");
        updateLoadMore(filtered.length);
    }

    function updateLoadMore(total) {
        const button = document.getElementById("loadMoreBtn");
        if (!button) {
            return;
        }

        const remaining = total - state.visible;
        if (remaining > 0) {
            button.hidden = false;
            button.textContent = "Ver más destinos (" + remaining + " restantes)";
        } else {
            button.hidden = true;
        }
    }

    function setupLoadMore() {
        const button = document.getElementById("loadMoreBtn");
        if (!button) {
            return;
        }

        button.addEventListener("click", function () {
            state.visible += EXPAND_STEP;
            renderJourneys();
        });
    }

    function updateHeroStats() {
        const externalCount = journeys.filter(function (item) {
            return item.external;
        }).length;

        const values = {
            journeyCount: journeys.length,
            externalCount: externalCount,
            featuredCount: featuredDestinations.length
        };

        Object.keys(values).forEach(function (key) {
            const element = document.getElementById(key);
            if (element) {
                element.textContent = String(values[key]);
            }
        });
    }

    function setupFilters() {
        const filterButtons = document.querySelectorAll(".chip[data-filter]");
        filterButtons.forEach(function (button) {
            button.addEventListener("click", function () {
                state.filter = button.getAttribute("data-filter") || "all";
                filterButtons.forEach(function (item) {
                    item.classList.toggle("active", item === button);
                    /* aria-pressed hace que un lector de pantalla anuncie el
                       estado del filtro (pulsado / no pulsado). Sin esto, la
                       clase "active" es solo visual y quien navega con lector
                       no sabe si el filtro cambio. */
                    item.setAttribute("aria-pressed", String(item === button));
                });
                state.visible = EXPAND_STEP;
                renderJourneys();
            });
        });

        const searchInput = document.getElementById("journeySearch");
        if (searchInput) {
            searchInput.addEventListener("input", function () {
                state.query = searchInput.value;
                state.visible = EXPAND_STEP;
                renderJourneys();
            });
        }
    }

    function setupHeader() {
        const header = document.getElementById("siteHeader");
        const navToggle = document.getElementById("navToggle");
        const navLinks = document.querySelectorAll(".site-nav a");

        function syncHeader() {
            if (!header) {
                return;
            }

            header.classList.toggle("is-scrolled", window.scrollY > 12);
        }

        syncHeader();
        window.addEventListener("scroll", syncHeader, { passive: true });

        if (navToggle) {
            navToggle.addEventListener("click", function () {
                const isOpen = document.body.classList.toggle("nav-open");
                navToggle.setAttribute("aria-expanded", String(isOpen));
                /* El nombre cambia con el estado: "Abrir menu" cerrado,
                   "Cerrar menu" abierto. Con solo aria-expanded, el lector
                   anuncia el estado pero el nombre queda incongruente. */
                navToggle.setAttribute("aria-label", isOpen ? "Cerrar menú de navegación" : "Abrir menú de navegación");
            });
        }

        navLinks.forEach(function (link) {
            link.addEventListener("click", function () {
                document.body.classList.remove("nav-open");
                if (navToggle) {
                    navToggle.setAttribute("aria-expanded", "false");
                }
            });
        });

        const sections = Array.from(document.querySelectorAll("main section[id]"));
        if (!sections.length) {
            return;
        }

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }

                const id = entry.target.getAttribute("id");
                navLinks.forEach(function (link) {
                    link.classList.toggle("is-active", link.getAttribute("href") === "#" + id);
                });
            });
        }, {
            rootMargin: "-45% 0px -45% 0px",
            threshold: 0
        });

        sections.forEach(function (section) {
            observer.observe(section);
        });
    }

    function setupRevealAnimations() {
        const revealNodes = document.querySelectorAll("[data-reveal]");
        revealNodes.forEach(function (node) {
            node.classList.add("reveal-pending");
        });

        if (reduceMotion) {
            revealNodes.forEach(function (node) {
                node.classList.add("is-visible");
                node.classList.remove("reveal-pending");
            });
            return;
        }

        if (!("IntersectionObserver" in window)) {
            revealNodes.forEach(function (node) {
                node.classList.add("is-visible");
                node.classList.remove("reveal-pending");
            });
            return;
        }

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add("is-visible");
                entry.target.classList.remove("reveal-pending");
                observer.unobserve(entry.target);
            });
        }, {
            threshold: 0.18,
            rootMargin: "0px 0px -12% 0px"
        });

        revealNodes.forEach(function (node) {
            observer.observe(node);
        });

        window.setTimeout(function () {
            revealNodes.forEach(function (node) {
                if (!node.classList.contains("is-visible")) {
                    node.classList.add("is-visible");
                    node.classList.remove("reveal-pending");
                }
            });
        }, 1400);
    }

    function setupSpotlightTilt() {
        const spotlight = document.getElementById("heroSpotlight");
        if (!spotlight || reduceMotion || !finePointer) {
            return;
        }

        spotlight.addEventListener("pointermove", function (event) {
            const bounds = spotlight.getBoundingClientRect();
            const x = (event.clientX - bounds.left) / bounds.width;
            const y = (event.clientY - bounds.top) / bounds.height;
            const rotateY = (x - 0.5) * 10;
            const rotateX = (0.5 - y) * 8;
            spotlight.style.transform = "perspective(1100px) rotateX(" + rotateX.toFixed(2) + "deg) rotateY(" + rotateY.toFixed(2) + "deg) translateY(-2px)";
        });

        spotlight.addEventListener("pointerleave", function () {
            spotlight.style.transform = "";
        });
    }


    function setupContactValidation() {
        const form = document.getElementById("contact-form");
        const feedback = document.getElementById("formFeedback");
        if (!form || !feedback) {
            return;
        }

        const nameInput = form.querySelector("#name");
        const emailInput = form.querySelector("#email");
        const titleInput = form.querySelector("#title1");
        const messageInput = form.querySelector("#message");
        const fields = [nameInput, emailInput, titleInput, messageInput].filter(Boolean);

        function setFeedback(message, type) {
            feedback.textContent = message;
            feedback.classList.remove("is-error", "is-success");
            if (type) {
                feedback.classList.add(type);
            }
        }

        function markField(field, valid) {
            if (!field) {
                return;
            }

            field.setAttribute("aria-invalid", String(!valid));
        }

        function validate() {
            let valid = true;

            const nameOk = !!nameInput && nameInput.value.trim().length >= 2;
            const emailOk = !!emailInput && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
            const titleOk = !!titleInput && titleInput.value.trim().length >= 3;
            const messageOk = !!messageInput && messageInput.value.trim().length >= 10;

            markField(nameInput, nameOk);
            markField(emailInput, emailOk);
            markField(titleInput, titleOk);
            markField(messageInput, messageOk);

            valid = nameOk && emailOk && titleOk && messageOk;

            if (!valid) {
                setFeedback("Revisa nombre, email, asunto y mensaje antes de lanzar la botella.", "is-error");
            } else {
                setFeedback("Todo listo. El mensaje puede salir con el viento.", "is-success");
            }

            return valid;
        }

        fields.forEach(function (field) {
            field.addEventListener("input", function () {
                if (field.getAttribute("aria-invalid") === "true") {
                    validate();
                }
            });
        });

        const tokenField = form.querySelector('#csrf_token');
        const submitBtn = document.getElementById('submitBtn');
        let sending = false;

        form.addEventListener('submit', function (event) {
            event.preventDefault();
            if (sending || !validate()) {
                return;
            }

            sending = true;
            if (submitBtn) {
                submitBtn.disabled = true;
            }
            setFeedback("Enviando mensaje...", "is-success");

            /* El token CSRF se pide al cargar la pagina, pero puede no haber
               llegado todavia (o haberse caducado la sesion). Se espera aqui,
               ya que sin el contacto.php responde siempre 403. */
            const tokenReady = (window.txopoCsrfToken || Promise.resolve(''))
                .catch(function () { return ''; })
                .then(function (token) {
                    if (tokenField && token) {
                        tokenField.value = token;
                    }
                });

            tokenReady
                .then(function () {
                    const formData = new FormData(form);
                    formData.set('ajax', '1');
                    return fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        credentials: 'same-origin',
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    });
                })
                .then(function (response) {
                    /* 404/405 significan que el endpoint PHP no existe donde se
                       esta sirviendo la pagina (alojamiento estatico sin PHP).
                       En ese caso es mejor ofrecer el correo directo que un
                       error tecnico que el visitante no puede resolver. */
                    if (response.status === 404 || response.status === 405) {
                        return { success: false, sinServidor: true };
                    }
                    return response.json().catch(function () {
                        return { success: false, message: 'respuesta no válida del servidor' };
                    });
                })
                .then(function (data) {
                    if (data && data.success) {
                        feedback.classList.remove("is-error");
                        feedback.classList.add("is-success");
                        feedback.innerHTML = '<div class="success-message">¡Mensaje enviado con éxito! Gracias por escribir.</div>';
                        form.reset();
                        /* reset() devuelve los campos a su valor del HTML, que en
                           el token es vacio: hay que volver a ponerlo. */
                        if (tokenField) {
                            tokenField.value = "";
                        }
                        if (typeof window.txopoRefreshCsrf === 'function') {
                            window.txopoRefreshCsrf();
                        }
                    } else if (data && data.sinServidor) {
                        setFeedback("", null);
                        feedback.classList.add("is-error");
                        feedback.innerHTML = '<div>Ahora mismo no se puede enviar el mensaje desde aquí. Escríbeme directamente a <a href="mailto:tkplts@gmail.com">tkplts@gmail.com</a>.</div>';
                    } else {
                        setFeedback("Hubo un problema al enviar: " + ((data && data.message) || "inténtalo de nuevo"), "is-error");
                    }
                })
                .catch(function () {
                    setFeedback("Error de conexión al enviar el mensaje.", "is-error");
                })
                .then(function () {
                    sending = false;
                    if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                });
        });
    }

    function setFooterYear() {
        const footerYear = document.getElementById("footerYear");
        if (footerYear) {
            footerYear.textContent = String(new Date().getFullYear());
        }
    }

    function setupScrollTop() {
        const scrollTopBtn = document.getElementById('scrollTopBtn');
        if (!scrollTopBtn) return;
        window.addEventListener('scroll', () => {
            scrollTopBtn.classList.toggle('visible', window.scrollY > 500);
        });
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    function setupTypewriter() {
        const el = document.querySelector('.typewriter');
        if (!el || reduceMotion) return;

        const text = el.textContent;
        /* El efecto vacia el h1 y escribe letra a letra: un lector de pantalla
           se encontraria un titular vacio y luego un ruido de actualizaciones
           caoticas. aria-label fija el nombre accesible al texto completo,
           asi el lector lo lee de una vez y el efecto visual sigue igual. */
        el.setAttribute('aria-label', text);
        el.textContent = '';
        // Mostramos el elemento por si estaba oculto y añadimos cursor por CSS
        el.classList.add('is-typing');
        
        let i = 0;
        // Escritura rápida: todo el titular visible en ~1.2s
        setTimeout(() => {
            const interval = setInterval(() => {
                if (i < text.length) {
                    el.textContent += text.charAt(i);
                    i++;
                } else {
                    clearInterval(interval);
                    el.classList.remove('is-typing'); // quita el cursor al acabar si se quiere
                }
            }, 18);
        }, 150);
    }

    function init() {
        renderFeatured();
        updateHeroStats();
        renderJourneys();
        setupFilters();
        setupLoadMore();
        setupHeader();
        setupRevealAnimations();
        setupSpotlightTilt();

        setupContactValidation();
        setupScrollTop();
        setupTypewriter();
        setFooterYear();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // Preloader: se oculta en cuanto la página carga (mínimo 400ms para evitar parpadeo)
    window.addEventListener('load', () => {
        setTimeout(() => {
            const preloader = document.getElementById('preloader');
            if (preloader) preloader.classList.add('hidden');
        }, 400);
    });
})();
