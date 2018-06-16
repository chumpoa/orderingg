"""Test e2e."""
import unittest
import os
import time
import threading

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# from werkzeug.serving import make_server

from app import create_app, db
from app.models import Product, Order, OrderProduct

basedir = os.path.abspath(os.path.dirname(__file__))


class Ordering(unittest.TestCase):
    """Clase Orderingg."""

    # Creamos la base de datos de test
    def setUp(self):
        """Set Up."""
        db = 'test.db'
        self.app = create_app()
        self.app.config.update(
            SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, db),
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
        """Test titulo."""
        driver = self.driver
        driver.get(self.baseURL)
        prodboton = '/html/body/main/div[1]/div/button'
        add_product_button = driver.find_element_by_xpath(prodboton)
        add_product_button.click()
        modal = driver.find_element_by_id('modal')
        assert modal.is_displayed(), "El modal no esta visible"

    def tearDown(self):
        """Tear Down."""
        self.driver.get('http://localhost:5000/shutdown')

        db.session.remove()
        db.drop_all()
        self.driver.close()
        self.app_context.pop()

    def test_modal_editar(self):
        """Test modal editar."""
        driver = self.driver
        driver.get(self.baseURL)
        time.sleep(10)
        orden = Order(id=1)
        db.session.add(orden)
        prod = Product(id=1, name='articulo', price=100)
        db.session.add(prod)
        op = OrderProduct(order_id=1, product_id=1, quantity=5, product=prod)
        db.session.add(op)
        db.session.commit()
        editbtn = '//*[@id="orders"]/table/tbody/tr[1]/td[6]/button[1]'
        botoneditar = driver.find_element_by_xpath(editbtn)
        botoneditar.click()
        time.sleep(5)
        nombre = driver.find_element_by_id('select-prod')
        cantidad = driver.find_element_by_id('quantity')
        time.sleep(5)
        self.assertNotEqual(nombre, ''), 'no hay elementos en el modal'
        self.assertNotEquals(cantidad, ''), 'no hay elementos en el modal'

    def test_cantidades_negativas(self):
        """Cantidades negativas test."""
        # Creamos una orden #
        orden = Order(id=1)
        # Cargamos la orden #
        db.session.add(orden)
        # Agregamos un poducto para poder probar el boton
        producto = Product(id=1, name='test', price=100)
        db.session.add(producto)
        db.session.commit()

        driver = self.driver
        driver.get(self.baseURL)

        # clicea en boton agregar
        agregabtn = '/html/body/main/div[1]/div/button'
        boton_agregar = driver.find_element_by_xpath(agregabtn)
        boton_agregar.click()
        elesele = '//*[@id="select-prod"]/option[2]'
        boton_seleccionar = driver.find_element_by_xpath(elesele)
        boton_seleccionar.click()
        boton_cantidad = driver.find_element_by_id('quantity')
        boton_cantidad.clear()
        boton_cantidad.send_keys("-4")
        elemen = '//*[@id="modal"]/div[2]/section/form/div[2]/div/p'
        mensaje = driver.find_element_by_xpath(elemen)
        self.assertTrue(mensaje.is_displayed())

    def test_borrar(self):
        """Test Borrar."""
        driver = self.driver
        driver.get(self.baseURL)
        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='Test', price=100)
        db.session.add(producto)
        ordenproducto = OrderProduct(order_id=1, product_id=1, quantity=1)
        db.session.add(ordenproducto)
        db.session.commit()

        driver.get(self.baseURL)
        eleborrar = '//*[@id="orders"]/table/tbody/tr[1]/td[6]/button[2]'
        botonborrar = driver.find_element_by_xpath(eleborrar)
        botonborrar.click()
        time.sleep(2)
        driver.refresh()
        driver.get(self.baseURL)
        noesta = False
        try:
            ele = '//*[@id="orders"]/table/tbody/tr[1]/td[2]'
            webdriver.find_element_by_xpath(ele)
        except NoSuchElementException:
            noesta = True

        assert noesta == True, "Fallo el test"


if __name__ == "__main__":
    unittest.main()
