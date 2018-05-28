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

            "id" : 1
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
        
if __name__ == '__main__':
    unittest.main()
