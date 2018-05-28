import unittest
import os
import time
import threading

from selenium import webdriver

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))

from werkzeug.serving import make_server

class Ordering(unittest.TestCase):
    # Creamos la base de datos de test
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'test.db'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True
        )

        self.app_context = self.app.app_context()
        self.app_context.push()

        self.baseURL = 'http://localhost:5000'

        db.session.commit()
        db.drop_all()
        db.create_all()

        self.t = threading.Thread(target=self.app.run)
        self.t.start()

        time.sleep(1)

        self.driver = webdriver.Chrome()


#!

    def test_borrar(self):

        orden = Order(id= 1)
        db.session.add(orden)
        producto = Product(id= 1, name= 'Producto', price= 10)
        db.session.add(producto)
        OrdenDeProducto = OrderProduct(order_id= 1, product_id= 1, quantity= 1, product= producto)
        db.session.add(OrdenDeProducto)
        db.session.commit()
        driver = self.driver
        driver.get(self.baseURL)
        btn = driver.find_element_by_id('btnborrar')
        btn.click()
        self.assertRaises(NoSuchElementException, driver.find_element_by_xpath, '//*[@id="orders"]/table/tbody/tr')

if __name__ == "__main__":
    unittest.main()

