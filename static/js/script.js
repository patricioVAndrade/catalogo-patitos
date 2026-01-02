document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const cards = document.getElementsByClassName('product-card');
    // --- 1. FUNCIÓN DE BÚSQUEDA ---
    function performSearch() {
        const query = searchInput.value.toLowerCase().trim();

        Array.from(cards).forEach(card => {
            const name = card.getAttribute('data-name').toLowerCase();
            const category = card.getAttribute('data-category').toLowerCase();
            const visibleText = card.innerText.toLowerCase(); 

            if (name.includes(query) || category.includes(query) || visibleText.includes(query)) {
                card.style.display = ''; // Mostrar (quita el display:none)
            } else {
                card.style.display = 'none'; // Ocultar
            }
        });
    }

    // --- 2. EVENTO AL TECLEAR (Lo que ya tenías) ---
    searchInput.addEventListener('input', performSearch);

    // --- 3. CORRECCIÓN DEL ERROR F5 (¡ESTO ES LO NUEVO!) ---
    // Al cargar la página, forzamos una revisión:
    // Si el navegador guardó texto, filtramos. Si está vacío, mostramos todo.
    function forzarReseteo() {
        // Solo si el buscador está visualmente vacío
        if (searchInput.value.trim() === "") {
            Array.from(cards).forEach(card => {
                // Forzamos la propiedad de estilo para asegurarnos que se vea
                card.style.removeProperty('display');
                card.style.display = ''; 
            });
        } else {
            // Si el navegador recordó el texto, aplicamos el filtro de nuevo
            performSearch();
        }
    }
    forzarReseteo();

    setTimeout(forzarReseteo, 50);
    setTimeout(forzarReseteo, 100);
});

$(document).ready(function () {
    
    // Inicializar DataTables (Buscador y Paginación)
    var table = $('#tablaCatalogo').DataTable({
        "stateSave": true, // Recuerda la página si recargan
        "pageLength": 15,  // Muestra 15 productos por página
        "ordering": false, // Desactivar ordenamiento automático
        "pagingType": "simple_numbers",
        "dom": 'rt<"mt-4 text-center"p>',
        "language": { 
            "search": "", 
            "searchPlaceholder": "Buscar Artículo        🔍", 
            "zeroRecords": "No encontramos ese artículo 🧸",
            "paginate": { 
                // CAMBIO CLAVE: Usamos iconos en vez de palabras para ahorrar espacio
                "next": '<i class="bi bi-chevron-right"></i>', 
                "previous": '<i class="bi bi-chevron-left"></i>' 
            },
            "info": "_START_ a _END_ de _TOTAL_",
            "infoEmpty": "0 a 0",
            "infoFiltered": ""
        },
    });

    $('#buscadorPropio').on('keyup', function () {
        table.search(this.value).draw();
    });

    var estadoGuardado = table.state.loaded();
    
    if (estadoGuardado && estadoGuardado.search && estadoGuardado.search.search) {
        // Si hay una búsqueda guardada, la escribimos en el input para que coincida
        $('#buscadorPropio').val(estadoGuardado.search.search);
    }

    // Scroll suave hacia arriba al cambiar de página
    table.on('page.dt', function () {
        $('html, body').animate({
            scrollTop: $(".filtros-container").offset().top - 80 
        }, 100); 
    });

    // Filtro por Categoría (Select desplegable)
    
});

// Función para abrir la foto en grande (Modal)
function abrirZoom(el) {
    const url = el.dataset.foto;
    const titulo = el.dataset.nombre;
    $('#imagenGrande').attr('src', url);
    $('#tituloGrande').text(titulo);
    new bootstrap.Modal('#modalZoom').show();
}

// Carga Perezosa de Imágenes (Lazy Loading)
// Ayuda a que la página no se trabe cargando 1000 fotos de golpe
(function() {
  const imgs = document.querySelectorAll('.img-producto');
  imgs.forEach(img => {
    const onLoad = () => img.classList.add('is-loaded');
    if (img.complete) onLoad(); else img.addEventListener('load', onLoad, { once: true });
    img.addEventListener('error', onLoad, { once: true });
  });
})();

// Nueva función para el Dropdown Personalizado
function aplicarFiltro(elemento, criterio) {
    // 1. Actualizar el texto del botón principal
    const textoSeleccionado = $(elemento).text().trim();
    $('#btnFiltro span').text(textoSeleccionado);
    
    // 2. Marcar visualmente la opción activa
    $('.dropdown-item').removeClass('active bg-light text-primary');
    $(elemento).addClass('active bg-light text-primary');

    // 3. Resetear filtros anteriores de DataTables
    var table = $('#tablaCatalogo').DataTable();
    $.fn.dataTable.ext.search.pop(); // Sacamos filtros viejos

    // 4. Aplicar la lógica según qué botón apretaron
    if (criterio === 'SPECIAL_OFERTA') {
        // FILTRO DE OFERTAS
        $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
            // Buscamos el atributo data-es-oferta en la tarjeta
            const esOferta = $(table.row(dataIndex).node()).find('.card-producto').attr('data-es-oferta');
            return esOferta === 'si'; // Solo mostramos si dice 'si'
        });

    } else if (criterio === 'SPECIAL_NUEVO') {
        // FILTRO DE NUEVOS
        $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
            const esNuevo = $(table.row(dataIndex).node()).find('.card-producto').attr('data-es-nuevo');
            return esNuevo === 'si';
        });

    } else if (criterio !== "") {
        // FILTRO NORMAL (CATEGORÍA)
        $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
            // Busamos el texto dentro del badge de categoría
            const categoriaFila = $(table.row(dataIndex).node()).find('.badge-categoria').text().trim();
            return categoriaFila === criterio;
        });
    }

    // 5. Redibujar la tabla con el nuevo filtro aplicado
    table.draw();
}

// Función para filtros especiales (Oferta / Nuevo)
function aplicarFiltroEspecial(tipo) {
    const cards = document.querySelectorAll('.product-card');
    
    // Actualizar texto del botón
    let texto = "";
    if(tipo === 'oferta') texto = "🔥 Ofertas Imperdibles";
    if(tipo === 'nuevo') texto = "✨ Novedades";
    $('#btnFiltro span').text(texto);

    cards.forEach(card => {
        let mostrar = false;
        
        if (tipo === 'oferta') {
            // Buscamos si dentro de la tarjeta hay un elemento con la clase badge-oferta
            // O podemos usar un atributo data. Vamos a usar el texto visual por simplicidad.
            if (card.innerHTML.includes("OFERTA")) mostrar = true;
        } else if (tipo === 'nuevo') {
            // Buscamos si tiene la cinta ribbon-nuevo
            if (card.querySelector('.ribbon-nuevo')) mostrar = true;
        }

        if (mostrar) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}