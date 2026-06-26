from django.apps import apps
from django.test import SimpleTestCase


class InventarioModuloTest(SimpleTestCase):
    def test_modulo_inventario_registrado(self):
        app = apps.get_app_config('inventario')
        self.assertEqual(app.label, 'inventario')
