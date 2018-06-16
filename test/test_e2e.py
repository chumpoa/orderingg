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
        bAdd = '/html/body/main/div[1]/div/button'
        driver = self.driver
        driver.get(self.baseURL)
        add_product_button = driver.find_element_by_xpath(bAdd)
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
        bEdit = '//*[@id="orders"]/table/tbody/tr[1]/td[6]/button[1]'
        driver = self.driver
        driver.get(self.baseURL)
        time.sleep(10)
        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='articulo', price=100)
        db.session.add(producto)
        orderProduct = OrderProduct(order_id=1, product_id=1, quantity=5, product=producto)
        db.session.add(orderProduct)
        db.session.commit()
        botoneditar = driver.find_element_by_xpath(bEdit)
        botoneditar.click()
        time.sleep(5)
        nombre = driver.find_element_by_id('select-prod')
        cantidad = driver.find_element_by_id('quantity')
        time.sleep(5)
        self.assertNotEqual(nombre, ''), 'no hay elementos en el modal'
        self.assertNotEquals(cantidad, ''), 'no hay elementos en el modal'

    def test_cantidades_negativas(self):
        # Creamos una orden
        orden = Order(id=1)
        # Cargamos la orden
        db.session.add(orden)
        # Agregamos un poducto para poder probar el boton
        producto = Product(id=1, name='test', price=100)
        db.session.add(producto)
        db.session.commit()

        driver = self.driver
        driver.get(self.baseURL)

        # hace clic en boton agregar
        boton_agregar = driver.find_element_by_xpath('/html/body/main/div[1]/div/button')
        boton_agregar.click()
        # Dentro del modal agregar selecciona el producto a agregar
        boton_seleccionar = driver.find_element_by_xpath('//*[@id="select-prod"]/option[2]')
        boton_seleccionar.click()
        # Despues selecciona la cantidad y asigna una cantidad negativa
        boton_cantidad = driver.find_element_by_id('quantity')
        boton_cantidad.clear()
        boton_cantidad.send_keys("-4")
    # debajo de la cantidad se ve el mensaje
        mensaje = driver.find_element_by_xpath('//*[@id="modal"]/div[2]/section/form/div[2]/div/p')
        self.assertTrue(mensaje.is_displayed())

    def test_borrar(self):
        driver = self.driver
        driver.get(self.baseURL)
        orden = Order(id=1)
        db.session.add(orden)
        producto = Product(id=1, name='Test', price=100)
        db.session.add(producto)
        ordenProducto = OrderProduct(order_id=1, product_id=1, quantity=1)
        db.session.add(ordenProducto)
        db.session.commit()
        driver.get(self.baseURL)

    # Agarro nombre de tabla antes de borrar
        nombre1 = driver.find_element_by_xpath('//*[@id="orders"]/table/tbody/tr[1]/td[2]').text
        botonBorrar = driver.find_element_by_xpath('//*[@id="orders"]/table/tbody/tr[1]/td[6]/button[2]')
        botonBorrar.click()
        time.sleep(2)
        driver.get(self.baseURL)
        # Agarro el nombre de la tabla despues de borrar
        nombre2 = driver.find_element_by_xpath('//*[@id="orders"]/table/tbody/tr[1]/td[2]').text
        # Comparo si son distintos
        assert nombre1 != nombre2, "Fallo el test, no se borro correctamente"


if __name__ == "__main__":
    unittest.main()
