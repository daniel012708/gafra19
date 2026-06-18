from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from inventario.models import MateriaPrima
from productos.models import Categoria, IngredienteReceta, Producto, Receta
from proveedores.models import Proveedor
from usuario.models import Usuario

from .models import OrdenProduccion


class ProduccionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 'tester@example.com', 'pass')
        Usuario.objects.create(user=self.user, rol='logistica', telefono='3001234567', activo=True)
        self.proveedor = Proveedor.objects.create(
            nombre='ProvT',
            contacto='Carlos Rios',
            telefono='3001234567',
            email='p@e.com',
            direccion='d',
            ciudad='ci',
            pais='pa',
            tipo='Nacional',
        )
        self.categoria = Categoria.objects.create(nombre='CatT')
        self.producto = Producto.objects.create(
            nombre='ProdT',
            descripcion='d',
            categoria=self.categoria,
            precio_venta=2,
            stock_actual=0,
            activo=True,
        )
        self.receta = Receta.objects.create(producto=self.producto, descripcion='Receta base', activo=True)
        self.materia_prima = MateriaPrima.objects.create(
            nombre='Acero fino',
            descripcion='Insumo base',
            marca='Marca Z',
            proveedor=self.proveedor,
            precio_unitario=5,
            unidad_medida='kg',
            stock_actual=100,
            stock_minimo=5,
            activo=True,
        )
        IngredienteReceta.objects.create(
            receta=self.receta,
            materia_prima=self.materia_prima,
            cantidad_requerida=2,
        )

    def test_create_produccion_via_view(self):
        self.client.login(username='tester', password='pass')
        resp = self.client.post(reverse('produccion:create'), {
            'producto': self.producto.pk,
            'cantidad_a_producir': 5,
            'notas': 'test',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(OrdenProduccion.objects.filter(producto=self.producto, cantidad_a_producir=5).exists())

    def test_update_produccion_via_view(self):
        self.client.login(username='tester', password='pass')
        orden = OrdenProduccion.objects.create(
            producto=self.producto,
            receta=self.receta,
            cantidad_a_producir=2,
            responsable=self.user,
            notas='Inicial',
        )
        resp = self.client.post(reverse('produccion:update', args=[orden.pk]), {
            'producto': self.producto.pk,
            'cantidad_a_producir': 10,
            'notas': 'updated',
        })
        self.assertEqual(resp.status_code, 302)
        orden.refresh_from_db()
        self.assertEqual(orden.cantidad_a_producir, 10)
        self.assertEqual(orden.notas, 'updated')

    def test_delete_produccion_via_view(self):
        self.client.login(username='tester', password='pass')
        orden = OrdenProduccion.objects.create(
            producto=self.producto,
            receta=self.receta,
            cantidad_a_producir=3,
            responsable=self.user,
        )
        resp = self.client.post(reverse('produccion:delete', args=[orden.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(OrdenProduccion.objects.filter(pk=orden.pk).exists())
