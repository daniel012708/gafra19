from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from clientes.models import Cliente
from productos.models import Categoria, Producto

from .models import DetalleVenta, Venta


class VentasViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.categoria = Categoria.objects.create(nombre='C1')
        self.producto = Producto.objects.create(
            nombre='ProdZ',
            descripcion='',
            categoria=self.categoria,
            precio_venta=200,
            stock_actual=10,
            activo=True,
        )
        self.cliente = Cliente.objects.create(
            nombre='Cliente',
            documento='123',
            direccion='Dir',
            telefono='3000000000',
            email='cliente@example.com',
        )
        self.venta = Venta.objects.create(
            vendedor=self.user,
            cliente=self.cliente,
            estado='pendiente',
            descuento=0,
            impuesto=0,
            total=100,
        )
        DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.producto,
            cantidad=1,
            precio_unitario=Decimal('200'),
            subtotal=Decimal('200'),
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('ventas:lista'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_items(self):
        self.client.login(username='tester', password='pass')
        response = self.client.get(reverse('ventas:lista'))
        self.assertContains(response, self.venta.numero_venta)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.client.login(username='tester', password='pass')
        response = self.client.post(reverse('ventas:crear'), {
            'cliente': self.cliente.id,
            f'cantidad_{self.producto.id}': '2',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ventas:confirmar'))

        confirm_response = self.client.post(reverse('ventas:confirmar'))
        self.assertEqual(confirm_response.status_code, 302)

        venta = Venta.objects.exclude(pk=self.venta.pk).first()
        self.assertIsNotNone(venta)
        self.assertEqual(venta.total, Decimal('400'))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 8)

