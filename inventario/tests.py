from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from productos.models import Categoria, Producto
from .models import Inventario


class InventarioViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        cat = Categoria.objects.create(nombre='CatTest')
        prod = Producto.objects.create(codigo='X1', nombre='ProdX', descripcion='', categoria=cat, precio_costo=1, precio_venta=2, activo=True)
        self.inv = Inventario.objects.create(producto=prod, cantidad_actual=10, cantidad_minima=1, cantidad_maxima=20, ubicacion='A1')

    def test_list_requires_login(self):
        response = self.client.get(reverse('inventario:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_items(self):
        self.client.login(username='tester', password='pass')
        response = self.client.get(reverse('inventario:list'))
        self.assertContains(response, 'ProdX')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.client.login(username='tester', password='pass')
        # create a different product to avoid one-to-one conflict
        new_cat = Categoria.objects.create(nombre='Another')
        prod2 = Producto.objects.create(
            codigo='Y2', nombre='ProdY', descripcion='', categoria=new_cat, precio_costo=1, precio_venta=2, activo=True
        )
        data = {'producto': prod2.id, 'cantidad_actual':5, 'cantidad_minima':0, 'cantidad_maxima':10, 'ubicacion':'B2'}
        response = self.client.post(reverse('inventario:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Inventario.objects.filter(ubicacion='B2').exists())
