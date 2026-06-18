from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from productos.models import Producto, Categoria
from proveedores.models import Proveedor
from clientes.models import Cliente
from .models import Venta, DetalleVenta


class VentasFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('vuser', 'v@example.com', 'pass')
        self.proveedor = Proveedor.objects.create(nombre='Prov', contacto='c', telefono='t', email='p@test.com', direccion='d', ciudad='ci', pais='pa')
        self.categoria = Categoria.objects.create(nombre='C1')
        self.producto = Producto.objects.create(codigo='PX', nombre='ProdX', descripcion='d', categoria=self.categoria, proveedor=self.proveedor, precio_costo=10, precio_venta=100)
        self.cliente = Cliente.objects.create(nombre='ClienteTest', documento='123', direccion='d', telefono='t', email='c@test.com')

    def test_create_venta_with_details(self):
        self.client.login(username='vuser', password='pass')
        url = reverse('ventas:crear')
        data = {
            'cliente': self.cliente.pk,
            'vendedor': self.user.pk,
            'estado': 'completada',
            'impuesto': '0',
            'descuento': '0',
            'total': '0',
            'observaciones': 'test',
            # formset management
            'detalles-TOTAL_FORMS': '1',
            'detalles-INITIAL_FORMS': '0',
            'detalles-MIN_NUM_FORMS': '0',
            'detalles-MAX_NUM_FORMS': '1000',
            'detalles-0-producto': self.producto.pk,
            'detalles-0-cantidad': '2',
            'detalles-0-precio_unitario': '100',
            'detalles-0-subtotal': '200',
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        v = Venta.objects.first()
        self.assertIsNotNone(v)
        self.assertTrue(v.numero_venta.startswith('V'))
        self.assertEqual(v.total, 200)from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from productos.models import Categoria, Producto
from .models import Venta, DetalleVenta


class VentasViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        cat = Categoria.objects.create(nombre='C1')
        prod = Producto.objects.create(codigo='Z1', nombre='ProdZ', descripcion='', categoria=cat, precio_costo=1, precio_venta=2, activo=True)
        self.venta = Venta.objects.create(
            numero_venta='V001', vendedor=self.user, cliente_nombre='Cliente',
            cliente_email='c@c.com', cliente_telefono='123', estado='pendiente',
            descuento=0, impuesto=0, total=100
        )
        DetalleVenta.objects.create(venta=self.venta, producto=prod, cantidad=1, precio_unitario=2, subtotal=2)

    def test_list_requires_login(self):
        response = self.client.get(reverse('ventas:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_items(self):
        self.client.login(username='tester', password='pass')
        response = self.client.get(reverse('ventas:list'))
        self.assertContains(response, 'V001')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.client.login(username='tester', password='pass')
        cat2 = Categoria.objects.create(nombre='C2')
        prod2 = Producto.objects.create(codigo='Z2', nombre='ProdZ2', descripcion='', categoria=cat2, precio_costo=1, precio_venta=2, activo=True)
        data = {
            'numero_venta': 'V002', 'vendedor': self.user.id, 'cliente_nombre': 'Cl2',
            'cliente_email': 'd@d.com', 'cliente_telefono': '456', 'estado': 'pendiente',
            'descuento':0, 'impuesto':0, 'total':50,
            'detalles-TOTAL_FORMS': '1',
            'detalles-INITIAL_FORMS': '0',
            'detalles-MIN_NUM_FORMS': '0',
            'detalles-MAX_NUM_FORMS': '1000',
            'detalles-0-producto': prod2.id,
            'detalles-0-cantidad': '1',
            'detalles-0-precio_unitario': '2',
            'detalles-0-subtotal': '2',
        }
        response = self.client.post(reverse('ventas:crear'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Venta.objects.filter(numero_venta='V002').exists())

