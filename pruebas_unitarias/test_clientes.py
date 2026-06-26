from django.apps import apps
from django.test import SimpleTestCase


class ClientesModuloTest(SimpleTestCase):
    def test_modulo_clientes_registrado(self):
        app = apps.get_app_config('clientes')
        self.assertEqual(app.label, 'clientes')
