from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from proveedores.models import Proveedor
from productos.models import Categoria, Producto
from .models import Produccion


class ProduccionViewTests(TestCase):
    def setUp(self):
        # create user
        self.user = User.objects.create_user('tester', 'tester@example.com', 'pass')
        # create related objects
        self.proveedor = Proveedor.objects.create(nombre='ProvT', contacto='c', telefono='t', email='p@e.com', direccion='d', ciudad='ci', pais='pa')
        self.categoria = Categoria.objects.create(nombre='CatT')
        self.producto = Producto.objects.create(codigo='C1', nombre='ProdT', descripcion='d', categoria=self.categoria, proveedor=self.proveedor, precio_costo=1, precio_venta=2)

    def test_create_produccion_via_view(self):
        self.client.login(username='tester', password='pass')
        url = reverse('produccion:create')
        data = {
            'proveedor': self.proveedor.pk,
            'producto': self.producto.pk,
            'cantidad': 5,
            'precio_unitario': '9.99',
            'nota': 'test'
        }
        resp = self.client.post(url, data)
        # expect redirect to list
        self.assertIn(resp.status_code, (302,))
        self.assertTrue(Produccion.objects.filter(proveedor=self.proveedor, producto=self.producto, cantidad=5).exists())

    def test_update_produccion_via_view(self):
        self.client.login(username='tester', password='pass')
        p = Produccion.objects.create(proveedor=self.proveedor, producto=self.producto, cantidad=2, precio_unitario=1.00)
        url = reverse('produccion:update', args=[p.pk])
        data = {
            'proveedor': self.proveedor.pk,
            'producto': self.producto.pk,
            'cantidad': 10,
            'precio_unitario': '5.00',
            'nota': 'updated'
        }
        resp = self.client.post(url, data)
        self.assertIn(resp.status_code, (302,))
        p.refresh_from_db()
        self.assertEqual(p.cantidad, 10)

    def test_delete_produccion_via_view(self):
        self.client.login(username='tester', password='pass')
        p = Produccion.objects.create(proveedor=self.proveedor, producto=self.producto, cantidad=3, precio_unitario=2.00)
        url = reverse('produccion:delete', args=[p.pk])
        resp = self.client.post(url)
        self.assertIn(resp.status_code, (302,))
        self.assertFalse(Produccion.objects.filter(pk=p.pk).exists())
