from django.apps import apps
from django.test import SimpleTestCase


class UsuarioModuloTest(SimpleTestCase):
    def test_modulo_usuario_registrado(self):
        app = apps.get_app_config('usuario')
        self.assertEqual(app.label, 'usuario')
