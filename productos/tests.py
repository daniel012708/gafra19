from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from inventario.models import MateriaPrima
from proveedores.models import Proveedor
from usuario.models import Usuario

from .models import Categoria, Producto


class ProductoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        Usuario.objects.create(user=self.user, rol='vendedor', telefono='3001234567', activo=True)
        self.cat = Categoria.objects.create(nombre='TestCat')
        self.proveedor = Proveedor.objects.create(
            nombre='Prov Test',
            contacto='Maria Lopez',
            telefono='3001234567',
            email='prov.test@example.com',
            direccion='Calle 5',
            ciudad='Bogota',
            pais='Colombia',
            tipo='Nacional',
        )
        self.materia_prima = MateriaPrima.objects.create(
            nombre='Madera sellada',
            descripcion='Insumo de prueba',
            marca='Bosque',
            proveedor=self.proveedor,
            precio_unitario=15,
            unidad_medida='kg',
            stock_actual=50,
            stock_minimo=5,
            activo=True,
        )
        self.prod = Producto.objects.create(
            nombre='Test Product', descripcion='desc',
            categoria=self.cat, precio_venta=2, activo=True
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
            'nombre': 'Another', 'descripcion': 'ok',
            'categoria': self.cat.id, 'precio_venta': 6,
            'ingredientes-TOTAL_FORMS': '1',
            'ingredientes-INITIAL_FORMS': '0',
            'ingredientes-MIN_NUM_FORMS': '0',
            'ingredientes-MAX_NUM_FORMS': '1000',
            'ingredientes-0-materia_prima': self.materia_prima.id,
            'ingredientes-0-cantidad_requerida': '1.5',
        }
        response = self.client.post(reverse('productos:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(nombre='Another').exists())

