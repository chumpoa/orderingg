import os
import unittest

from flask import json
from flask_testing import TestCase

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

class OrderingTestCase(TestCase):
    def create_app(self):
        config_name = 'testing'
        app = create_app()
        app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )
        return app

    # Creamos la base de datos de test
    def setUp(self):
        db.session.commit()
        db.drop_all()
        db.create_all()

    # Destruimos la base de datos de test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_iniciar_sin_productos(self):
        resp = self.client.get('/product')
        data = json.loads(resp.data)

        assert len(data) == 0, "La base de datos tiene productos"

    def test_crear_producto(self):
        data = {
            'name': 'Tenedor',
            'price': 50
        }

        resp = self.client.post('/product', data=json.dumps(data), content_type='application/json')

        # Verifica que la respuesta tenga el estado 200 (OK)
        self.assert200(resp, "Falló el POST")
        p = Product.query.all()

        # Verifica que en la lista de productos haya un solo producto
        self.assertEqual(len(p), 1, "No hay productos")


    def test_metodoPUT(self):
       #creo una orden y un producto
        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='articulo', price=100)
        db.session.add(producto)

    #creo un orderProduct
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=5, product=producto)
        db.session.add(orderProduct)
        db.session.commit()

       #se realiza un cambio en la DB
        orderProduct = {"quantity": 6, "product": {"id": 1}}
        self.client.put('/order/1/product/1', data=json.dumps(orderProduct), content_type='application/json')
        resp = self.client.get('/order/1/product/1')
        productoA=json.loads(resp.data)
        assert productoA['quantity'] == 6, "fallo el metodo PUT" #si el cambio impacto en la DB se pasa el test


    def test_totalPrice(self):
        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='articulo', price=100)
        db.session.add(producto)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=5, product=producto)
        db.session.add(orderProduct)
        db.session.commit()
        resp = self.client.get('/order/1/product/1')
        productoA = json.loads(resp.data)
        assert productoA['totalPrice'] == 500, "el precio no se calcula correctamente"


    def test_delete(self):
        data = {
            'id':1,
            'name': 'Tenedor',
            'price': 50
        }

        data1 = {
            'id':2,
            'name': 'sillon',
            'price': 500
        }

        self.client.post('/product', data=json.dumps(data), content_type='application/json')
        self.client.post('/product', data=json.dumps(data1), content_type='application/json')

        orden = {

            "id": 1
        }

        orden = Order()
        db.session.add(orden)
        db.session.commit()

        orderProduct =  {"quantity":1,"product":{"id":1}}
        self.client.post('/order/1/product', data=json.dumps(orderProduct), content_type='application/json')
        orderProduct =  {"quantity":1,"product":{"id":2}}
        self.client.post('/order/1/product', data=json.dumps(orderProduct), content_type='application/json')

        cantidad = self.client.get('order/1/product')
        self.client.delete('/order/1/product/2', data=json.dumps(orderProduct), content_type='application/json')
        cantidad2 = self.client.get('order/1/product')


        self.assertLess(cantidad2,cantidad , "No se borro correctamente el producto")


    def test_nombre_vacio(self):
        producto = {
            'id': 1,
            'name': 'jp',
            'price': 50
        }

        resp= self.client.post('/product', data=json.dumps(producto), content_type='application/json')
        assert resp.status_code != 201, "El producto puede ser vacio"

    def test_productos_negativos(self):
        #Cramos un producto
        producto = {
            'id': 1,
            'name': 'Producto test',
            'price': 100
        }

        self.client.post('/product', data=json.dumps(producto), content_type='application/json')
        #Creamos una orden
        orden = {
            'id': 1
        }

        #Cargamos la orden
        self.client.post('/order', data=json.dumps(orden), content_type='application/json')

        #Generamos un producto para agregar a la orden con cantidad negativa
        producto_orden =  {"quantity":-100,"product":{"id":1}}

        #Cargamos el producto a la orden
        resultado = self.client.post('/order/1/product/', data=json.dumps(producto_orden), content_type='application/json')

        #Tiene que tirar el error
        assert resultado.status_code != 201, "La cantidad no puede ser negativa"

    def test_metodo_GET(self):
        #Cargamos datos a la base para probar el metodo get
        #Cramos un producto
        producto = {
            'id': 1,
            'name': 'Producto test',
            'price': 100
        }

        self.client.post('/product', data=json.dumps(producto), content_type='application/json')
        #Creamos una orden
        orden = {
            'id': 1
        }

        #Cargamos la orden
        self.client.post('/order', data=json.dumps(orden), content_type='application/json')

        #Generamos un producto para agregar a la orden con cantidad negativa
        producto_orden =  {"quantity":-100,"product":{"id":1}}

        #Cargamos el producto a la orden
        self.client.post('/order/1/product/', data=json.dumps(producto_orden), content_type='application/json')
        #Se termina de cargar un producto a la orden

        #Se comienza a probar el metodo GET
        resp = self.client.get('/order/1/product/1')

        #Si el metodo GET funciona correctamente entonces la respuesta sera 200 entonces
        assert resp.status_code == 200, "El metodo GET no funciona"

if __name__ == '__main__':
    unittest.main()
