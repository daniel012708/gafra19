from django.apps import apps
from django.test import SimpleTestCase


class ProduccionModuloTest(SimpleTestCase):
    def test_modulo_produccion_registrado(self):
        app = apps.get_app_config('produccion')
        self.assertEqual(app.label, 'produccion')
