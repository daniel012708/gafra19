from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from proveedores.models import Proveedor
from usuario.models import Usuario

from .models import MateriaPrima


class InventarioViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        Usuario.objects.create(user=self.user, rol='almacenista', telefono='3001234567', activo=True)
        self.proveedor = Proveedor.objects.create(
            nombre='Proveedor Base',
            contacto='Ana Ruiz',
            telefono='3001234567',
            email='proveedor.base@example.com',
            direccion='Calle 1',
            ciudad='Bogota',
            pais='Colombia',
            tipo='Nacional',
            activo=True,
        )
        self.materia_prima = MateriaPrima.objects.create(
            nombre='Tela premium',
            descripcion='Tela de prueba',
            marca='Marca X',
            proveedor=self.proveedor,
            precio_unitario=10,
            unidad_medida='kg',
            stock_actual=10,
            stock_minimo=2,
            ubicacion='A1',
            activo=True,
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('inventario:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_items(self):
        self.client.login(username='tester', password='pass')
        response = self.client.get(reverse('inventario:list'))
        self.assertContains(response, 'Tela premium')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.client.login(username='tester', password='pass')
        data = {
            'nombre': 'Espuma HR',
            'descripcion': 'Espuma de alta densidad',
            'marca': 'Marca Y',
            'proveedor': self.proveedor.id,
            'precio_unitario': '25.50',
            'unidad_medida': 'kg',
            'stock_actual': '15',
            'stock_minimo': '3',
            'ubicacion': 'B2',
            'observaciones': 'Ingreso inicial',
            'activo': 'on',
        }
        response = self.client.post(reverse('inventario:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MateriaPrima.objects.filter(nombre='Espuma HR').exists())
