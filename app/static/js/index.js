(function () {
    const $totalPrice = document.querySelector('#total-price');

    // Estado de la aplicacion
    const state = {
        products: API.getProducts(),
        selectedProduct: null,
        quantity: 0,
        order: API.getOrder()
    }

    const refs = {}

    /**
     * Actualiza el valor del precio total
     **/
    function updateTotalPrice() {
        const totalPrice = state.selectedProduct.price * state.quantity;
        $totalPrice.innerHTML = `Precio total: $ ${totalPrice}`
    }

    /**
     * Dispara la actualizacion del precio total del producto
     * al cambiar el producto seleccionado
     **/
    function onProductSelect(selectedProduct) {
        state.selectedProduct = selectedProduct;
        updateTotalPrice();
    }

    /**
     * Dispara la actualizacion del precio total del producto
     * al cambiar la cantidad del producto
     **/
    function onChangeQunatity(quantity) {
        state.quantity = quantity;
        updateTotalPrice();
    }

    /**
     * Agrega un producto a una orden
     *
     **/
    function onAddProduct() {
        API.addProduct(1, state.selectedProduct, state.quantity)
            .then(function (r) {
                if (r.error) {
                    console.error(r.error);
                } else {
                    API.getOrder().then(function (data) {
                        refs.table.update(data);
                    });

                    refs.modal.close();
                }
            });

    }
      // edita un producto de una orden
    function onEditProduct() {
    const productId = document.getElementById('select-prod').value;
    const product = API.getOrderProduct(1,productId);

           API.editProduct(1,productId, state.quantity, product)
            .then(function (r) {
                if (r.error) {
                    console.error(r.error);
                } else {
                    API.getOrder().then(function (data) {

                        refs.table.update(data);
                        alert ("El producto fue modificado exitosamente");
                    });

                    refs.modal.close();
                }
            });
    }
    /**
     * Inicializa la aplicacion
     **/
    function init() {
        refs.modal = Modal.init({
            el: '#modal',
            products: state.products,
            onProductSelect: onProductSelect,
            onChangeQunatity: onChangeQunatity,
            onAddProduct: onAddProduct,
            onEditProduct: onEditProduct,
        });

        // Inicializamos la tabla
        refs.table = Table.init({
            el: '#orders',
            data: state.order
        });
    }

    init();
    window.refs = refs;
})()

