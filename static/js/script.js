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
function aplicarFiltro(elemento, categoria) {
    // 1. Actualizar el texto del botón principal
    const textoSeleccionado = $(elemento).text().trim();
    $('#btnFiltro span').text(textoSeleccionado);
    
    // 2. Marcar visualmente la opción activa
    $('.dropdown-item').removeClass('active bg-light text-primary');
    $(elemento).addClass('active bg-light text-primary');

    // 3. Aplicar el filtro en DataTables
    var table = $('#tablaCatalogo').DataTable();
    $.fn.dataTable.ext.search.pop();
    
    if (categoria !== "") {
        $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
            return $(table.row(dataIndex).node()).find('.badge-categoria').text() === categoria;
        });
    }
    table.draw();
}