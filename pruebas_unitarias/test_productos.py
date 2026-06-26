from django.apps import apps
from django.test import SimpleTestCase


class ProductosModuloTest(SimpleTestCase):
    def test_modulo_productos_registrado(self):
        app = apps.get_app_config('productos')
        self.assertEqual(app.label, 'productos')
