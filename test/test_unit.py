import os
import unittest

from flask import json
from flask_testing import TestCase

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

class OrderingTestCase(TestCase):
    def create_app(self):
        """Create app."""

        # config_name = 'testing'
        app = create_app()
        app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )
        return app

    # Creamos la base de datos de test
    def setUp(self):
        """Set up."""

        db.session.commit()
        db.drop_all()
        db.create_all()

    # Destruimos la base de datos de test
    def tearDown(self):
        """Tear down."""

        db.session.remove()
        db.drop_all()

    def test_iniciar_sin_productos(self):
        """Test iniciar sin producto."""

        resp = self.client.get('/product')
        data = json.loads(resp.data)

        assert len(data) == 0, "La base de datos tiene productos"

    def test_crear_producto(self):
        """Test crear producto."""

        data = {
            'name': 'Tenedor',
            'price': 50
        }

        app = 'application/json'
        p = '/product'
        resp = self.client.post(p, data=json.dumps(data), content_type=app)

        # Verifica que la respuesta tenga el estado 200 (OK)
        self.assert200(resp, "Fallo el POST")
        p = Product.query.all()
        # Verifica que en la lista de productos haya un solo producto
        self.assertEqual(len(p), 1, "No hay productos")

    def test_metodoPUT(self):
        """Test metodo put."""
        # creo una orden y un producto

        orden = Order(id=1)
        db.session.add(orden)
        p = Product(id=1, name='articulo', price=100)
        db.session.add(p)

        # creo un orderProduct
        op = OrderProduct(order_id=1, product_id=1, quantity=5, product=p)
        db.session.add(op)
        db.session.commit()

       # se realiza un cambio en la DB
        op = {"quantity": 6, "product": {"id": 1}}
        stringa = '/order/1/product/1'
        stringb = 'application/json'
        self.client.put(stringa, data=json.dumps(op), content_type=stringb)
        resp = self.client.get('/order/1/product/1')
        productoa = json.loads(resp.data)
        assert productoa['quantity'] == 6, "fallo el metodo PUT"
        # si el cambio impacto en la DB se pasa el test

    def test_totalPrice(self):
        """Test total price."""
        orden = Order(id=1)
        db.session.add(orden)
        p = Product(id=1, name='articulo', price=100)
        db.session.add(p)
        op = OrderProduct(order_id=1, product_id=1, quantity=5, product=p)
        db.session.add(op)
        db.session.commit()
        resp = self.client.get('/order/1/product/1')
        productoa = json.loads(resp.data)
        assert productoa['totalPrice'] == 500, "precio mal calculado"


    def test_delete(self):
        """Test delete."""
        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='articulo', price=100)
        db.session.add(producto)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=5, product=producto)
        db.session.add(orderProduct)
        db.session.commit()
        resp = self.client.delete('/order/1/product/1', content_type='application/json')
        assert resp.status_code == 200, "Erorr en DELETE"
        assert OrderProduct.query.limit(1).all() == [], "No borro el producto"




    def test_nombre_vacio(self):
        """Test nombre vacio."""
        producto = {
            'id': 1,
            'name': '',
            'price': 50
        }

        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='articulo', price=100)
        nombre = producto.name
        db.session.add(producto)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=5, product=producto)
        db.session.add(orderProduct)
        db.session.commit()
        assert producto["name"] != '', "El producto esta vacio"
        assert nombre != '', "El producto esta vacio"


    def test_productos_negativos(self):
        """Test productos negativos."""
        # Cramos un producto

        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='articulo', price=100)
        db.session.add(producto)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=-10, product=producto)
        db.session.add(orderProduct)
        db.session.commit()

        # Tiene que tirar el error
        cantidad = orderProduct.quantity
        assert cantidad > 0,  "La cantidad no puede ser negativa"

    def test_metodo_GET(self):
        # Cargamos datos a la base para probar el metodo get#
        # Cramos un producto#
        # Creamos una orden#
        orden = Order(id=1)
        # Cargamos la orden
        db.session.add(orden)
        # Agregamos un poducto#
        producto = Product(id=1, name='test', price=100)
        db.session.add(producto)
        # Agregamos el producto a la orden
        producto_orden = OrderProduct(order_id=1, product_id=1, quantity=5, product=producto)
        db.session.add(producto_orden)
        # S e termina de cargar un producto a la orden

        # Se comienza a probar el metodo GET
        resp = self.client.get('/order/1/product/1')

        # Si el metodo GET funciona correctamente entonces la respuesta sera 200 entonces
        assert resp.status_code == 200, "El metodo GET no funciona"
        data = json.loads(resp.data)
        assert data["id"] == 1, "El id no es el esperado"
        assert data["name"] == "test", "El nombre no es el esperado"
        assert data["price"] == 100, "El precio no es el esperado"
        assert data["quantity"] == 5, "La cantidad no es el esperado"
        assert data["totalPrice"] == 500, "El totalPrice no es el esperado"

    def test_borrar(self):

        """Test Borrar."""

        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='Producto', price=10)
        db.session.add(producto)
        ordendeproducto = OrderProduct(order_id=1, product_id=1, quantity=1, product=producto)
        db.session.add(ordendeproducto)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        btnelem = '/html/body/main/div[2]/div/table/tbody/tr[1]/td[6]/button[2]'
        btn = driver.find_element_by_xpath(btnelem)
        btn.click()
        xpath = '//*[@id="orders"]/table/tbody/tr'
        self.assertRaises(NoSuchElementException, driver.find_element_by_xpath, xpath)


if __name__ == '__main__':
    unittest.main()
