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

    def test_title(self):
        driver = self.driver
        driver.get(self.baseURL)
        add_product_button = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        add_product_button.click()
        modal = driver.find_element_by_id('modal')
        assert modal.is_displayed(), "El modal no esta visible"

    def tearDown(self):
        self.driver.get('http://localhost:5000/shutdown')

        db.session.remove()
        db.drop_all()
        self.driver.close()
        self.app_context.pop()

    def test_modal_editar(self):
        driver = self.driver
        driver.get(self.baseURL)
        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='articulo', price=100)
        db.session.add(producto)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=5, product=producto)
        db.session.add(orderProduct)
        db.session.commit()
        botoneditar = driver.find_element_by_xpath('//*[@id="orders"]/table/tbody/tr[1]/td[6]/button[1]')
        botoneditar.click()
        time.sleep(10)
        nombre = driver.find_element_by_id('select-prod')
        cantidad = driver.find_element_by_id('quantity')
        time.sleep(10)
        Assert.assertNotNul(nombre, cantidad), 'no hay elementos en el modal'
        time.sleep(10)


if __name__ == "__main__":
    unittest.main()