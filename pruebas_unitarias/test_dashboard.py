from django.apps import apps
from django.test import SimpleTestCase


class DashboardModuloTest(SimpleTestCase):
    def test_modulo_dashboard_registrado(self):
        app = apps.get_app_config('dashboard')
        self.assertEqual(app.label, 'dashboard')
