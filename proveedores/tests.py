from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Proveedor


class ProveedorViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.proveedor = Proveedor.objects.create(
            nombre='Prov T', contacto='C', telefono='123', email='a@b.com',
            direccion='Dir', ciudad='Ciudad', pais='Pais', activo=True
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('proveedores:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_items(self):
        self.client.login(username='tester', password='pass')
        response = self.client.get(reverse('proveedores:list'))
        self.assertContains(response, 'Prov T')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.client.login(username='tester', password='pass')
        data = {
            'nombre': 'Prov2', 'contacto':'X','telefono':'000','email':'x@x.com',
            'direccion':'D','ciudad':'C','pais':'P','activo': True
        }
        response = self.client.post(reverse('proveedores:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Proveedor.objects.filter(nombre='Prov2').exists())
