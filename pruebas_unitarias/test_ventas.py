from django.apps import apps
from django.test import SimpleTestCase


class VentasModuloTest(SimpleTestCase):
    def test_modulo_ventas_registrado(self):
        app = apps.get_app_config('ventas')
        self.assertEqual(app.label, 'ventas')
