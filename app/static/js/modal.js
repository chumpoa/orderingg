const Modal = (function () {

    /**
     * Abre el modal
     **/
    function open($modal,caso,producto) {
        const editTitle = document.getElementById('edit-title');
        const saveTitle = document.getElementById('save-title');
        const editButton = document.getElementById('edit-button');
        const saveButton = document.getElementById('save-button');

        switch(caso) {
        case "1":                                     //agrega un nuevo producto

        document.getElementById('select-prod').disabled=false;
        editButton.classList.add('is-hidden');
        editTitle.classList.add('is-hidden');
        saveButton.classList.remove('is-hidden');
        saveTitle.classList.remove('is-hidden');
        $modal.classList.add('is-active');

       break;

       case "2":                                    //edita un producto
        document.getElementById('select-prod').disabled=true;
        saveButton.classList.add('is-hidden');
        saveTitle.classList.add('is-hidden');
        editButton.classList.remove('is-hidden');
        editTitle.classList.remove('is-hidden');
        $modal.classList.add('is-active');
         API.getOrderProduct(1,producto).then(function (ProductoSeleccionado){            //completa los campos del modal con el producto seleccionado
         document.getElementById('quantity').value=ProductoSeleccionado["quantity"];
         var nombreProducto;
         nombreProducto = ProductoSeleccionado["name"];
         var valorSelect;
         switch(nombreProducto) {
         case "Silla":
         valorSelect=1;
         break;
         case "Mesa":
         valorSelect=2;
         break;
         case "Vaso":
         valorSelect=3;
         break;
         case "Individual":
         valorSelect=4;
         break;}
          document.getElementById("select-prod").value=valorSelect;
         });


           break; }

    }




    /**
     * Cierra el modal
     **/
    function close($modal) {
        $modal.classList.remove('is-active');
    }

    /**
     * Inicializa el modal de agregar producto
     **/
    function init(config) {
        const $modal = document.querySelector(config.el);

        // Inicializamos el select de productos
        Select.init({
            el: '#select',
            data: config.products,
            onSelect: config.onProductSelect
        });

        // Nos ponemos a escuchar cambios en el input de cantidad
        $modal.querySelector('#quantity')
            .addEventListener('input', function () {
                config.onChangeQunatity(this.value)
            });

        $modal.querySelector('#save-button')
            .addEventListener('click', config.onAddProduct);

        $modal.querySelector('#edit-button')
             .addEventListener('click', config.onEditProduct);

        return {
            close: close.bind(null, $modal),
            open: open.bind(null, $modal)
        }
    }

    return {
        init
    }
})();

