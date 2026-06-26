from django.apps import apps
from django.test import SimpleTestCase


class ProveedoresModuloTest(SimpleTestCase):
    def test_modulo_proveedores_registrado(self):
        app = apps.get_app_config('proveedores')
        self.assertEqual(app.label, 'proveedores')
