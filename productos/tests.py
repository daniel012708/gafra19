from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Categoria, Producto


class ProductoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.cat = Categoria.objects.create(nombre='TestCat')
        self.prod = Producto.objects.create(
            codigo='T001', nombre='Test Product', descripcion='desc',
            categoria=self.cat, precio_costo=1, precio_venta=2, activo=True
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('productos:list'))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_list_shows_items(self):
        self.client.login(username='tester', password='pass')
        response = self.client.get(reverse('productos:list'))
        self.assertContains(response, 'Test Product')
        self.assertEqual(response.status_code, 200)

    def test_create_product(self):
        self.client.login(username='tester', password='pass')
        data = {
            'codigo': 'T002', 'nombre': 'Another', 'descripcion': 'ok',
            'categoria': self.cat.id, 'precio_costo': 5, 'precio_venta': 6,
            'activo': True
        }
        response = self.client.post(reverse('productos:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(codigo='T002').exists())

