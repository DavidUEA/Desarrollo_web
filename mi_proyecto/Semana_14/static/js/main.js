document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-product-btn');
    const container = document.getElementById('detalle-productos');

    if (!addButton || !container) {
        return; // Salir si los elementos no existen
    }
    
    // Función auxiliar para reindexar ID y NAME de campos
    function updateElementIndex(elem, prefix, index) {
        // Expresión regular para encontrar el índice anterior
        const regex = new RegExp(`(${prefix}-\\d+-|${prefix}__\\d+__)`);
        
        // Actualizar NAME
        let name = elem.getAttribute('name');
        if (name) {
            elem.setAttribute('name', name.replace(regex, `${prefix}-${index}-`));
        }

        // Actualizar ID y for (para etiquetas)
        let id = elem.getAttribute('id');
        if (id) {
            elem.setAttribute('id', id.replace(regex, `${prefix}-${index}-`));
        }

        // Actualizar etiqueta 'for'
        if (elem.tagName === 'LABEL') {
             let htmlFor = elem.getAttribute('for');
             if (htmlFor) {
                elem.setAttribute('for', htmlFor.replace(regex, `${prefix}-${index}-`));
             }
        }
    }
    
    // Función principal para clonar y añadir un nuevo detalle
    addButton.addEventListener('click', function() {
        // Obtenemos la última fila como plantilla
        const lastDetail = container.lastElementChild;
        if (!lastDetail || !lastDetail.classList.contains('detalle-producto')) {
            // Si no hay detalles, o el primero no es correcto, no hacemos nada.
            return;
        }

        // Obtener el nuevo índice (el número de filas actuales)
        let totalDetails = container.children.length;
        
        // Clonar la última fila
        const newDetail = lastDetail.cloneNode(true); 
        
        // Limpiar y reindexar todos los campos del nuevo detalle
        newDetail.querySelectorAll('input, select, label').forEach(function(input) {
            if (input.tagName === 'INPUT' || input.tagName === 'SELECT') {
                 // Limpiar el valor solo para inputs y selects
                if (input.type !== 'hidden') {
                    input.value = ''; 
                }
            }
            // Aplicar la reindexación a todos los elementos relevantes
            updateElementIndex(input, 'detalles', totalDetails);
        });

        // Adjuntar el nuevo detalle al contenedor
        container.appendChild(newDetail);
    });
});