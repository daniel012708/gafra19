from django.core.management.base import BaseCommand
from proveedores.models import Proveedor
from productos.models import Producto, Categoria, Receta, IngredienteReceta
from clientes.models import Cliente
from inventario.models import MateriaPrima
from ventas.models import Venta, DetalleVenta
from produccion.models import OrdenProduccion
from django.contrib.auth.models import User
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Populate sample data for testing the production system'

    def handle(self, *args, **options):
        # Create a user
        user, _ = User.objects.get_or_create(username='sampleadmin', defaults={'email': 'admin@local'})

        # Proveedores
        provs = []
        for i in range(1, 6):
            p, _ = Proveedor.objects.get_or_create(
                nombre=f'Proveedor {i}',
                defaults={
                    'contacto': f'Contacto {i}',
                    'telefono': f'300000000{i}',
                    'email': f'proveedor{i}@test.com',
                    'direccion': f'Dirección {i}',
                    'ciudad': 'Bogotá',
                    'pais': 'Colombia'
                }
            )
            provs.append(p)

        # Categorías
        cats = []
        for nombre in ['Alimentos', 'Bebidas', 'Lácteos', 'Panadería', 'Carnes']:
            c, _ = Categoria.objects.get_or_create(nombre=nombre)
            cats.append(c)

        # Materias Primas
        materias = []
        materias_data = [
            ('Harina', 'Harina de trigo premium', 'KG', 50, 10, 2500),
            ('Azúcar', 'Azúcar refinada', 'KG', 100, 20, 1800),
            ('Leche', 'Leche fresca', 'L', 80, 15, 3200),
            ('Huevos', 'Huevos frescos', 'UNIDAD', 200, 50, 250),
            ('Mantequilla', 'Mantequilla sin sal', 'KG', 30, 5, 8500),
            ('Chocolate', 'Chocolate para repostería', 'KG', 25, 5, 12000),
            ('Canela', 'Canela en polvo', 'KG', 15, 3, 15000),
            ('Vainilla', 'Extracto de vainilla', 'ML', 40, 8, 25000),
        ]

        for nombre, desc, unidad, stock, minimo, precio in materias_data:
            mp, _ = MateriaPrima.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': desc,
                    'unidad_medida': unidad,
                    'stock_actual': stock,
                    'stock_minimo': minimo,
                    'precio_unitario': precio,
                    'proveedor': random.choice(provs),
                    'activo': True
                }
            )
            materias.append(mp)

        # Productos con recetas
        productos_data = [
            ('Pan Integral', 'Pan de harina integral', 'Panadería', [
                ('Harina', 0.5), ('Leche', 0.2), ('Huevos', 2), ('Mantequilla', 0.1)
            ]),
            ('Galleta de Chocolate', 'Galletas con chips de chocolate', 'Panadería', [
                ('Harina', 0.3), ('Azúcar', 0.2), ('Huevos', 1), ('Mantequilla', 0.15), ('Chocolate', 0.1)
            ]),
            ('Pastel de Vainilla', 'Pastel esponjoso de vainilla', 'Panadería', [
                ('Harina', 0.4), ('Azúcar', 0.3), ('Huevos', 3), ('Leche', 0.25), ('Mantequilla', 0.2), ('Vainilla', 5)
            ]),
            ('Bizcocho', 'Bizcocho tradicional', 'Panadería', [
                ('Harina', 0.35), ('Azúcar', 0.25), ('Huevos', 2), ('Leche', 0.15), ('Mantequilla', 0.1)
            ]),
        ]

        prods = []
        for nombre, desc, cat_nombre, ingredientes in productos_data:
            categoria = Categoria.objects.get(nombre=cat_nombre)
            prod, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': desc,
                    'categoria': categoria,
                    'precio_costo': random.randint(5000, 15000),
                    'precio_venta': random.randint(8000, 25000),
                    'stock_actual': random.randint(0, 50),
                    'activo': True
                }
            )
            prods.append(prod)

            # Crear receta
            receta, _ = Receta.objects.get_or_create(
                producto=prod,
                defaults={'activo': True}
            )

            # Agregar ingredientes
            for mat_nombre, cantidad in ingredientes:
                materia = next((m for m in materias if m.nombre == mat_nombre), None)
                if materia:
                    IngredienteReceta.objects.get_or_create(
                        receta=receta,
                        materia_prima=materia,
                        defaults={'cantidad_requerida': cantidad}
                    )

        # Clientes
        clients = []
        for i in range(1, 6):
            c, _ = Cliente.objects.get_or_create(
                nombre=f'Cliente {i}',
                defaults={
                    'documento': f'1000000{i}',
                    'direccion': f'Dirección {i}',
                    'telefono': f'30000000{i}',
                    'email': f'cliente{i}@example.com'
                }
            )
            clients.append(c)

        # Órdenes de producción de ejemplo
        for prod in prods[:2]:  # Solo para algunos productos
            if hasattr(prod, 'receta') and prod.receta.activo:
                orden = OrdenProduccion.objects.create(
                    producto=prod,
                    cantidad_a_producir=random.randint(10, 50),
                    responsable=user,
                    estado='PENDIENTE'
                )
                self.stdout.write(f'Orden de producción creada: {orden}')

        # Ventas de ejemplo
        for i in range(1, 6):
            v = Venta.objects.create(
                vendedor=user,
                cliente=random.choice(clients),
                estado='completada',
                impuesto=0
            )
            # Detalles de venta
            for _ in range(random.randint(1, 3)):
                prod = random.choice(prods)
                DetalleVenta.objects.create(
                    venta=v,
                    producto=prod,
                    cantidad=random.randint(1, 5),
                    precio_unitario=prod.precio_venta
                )

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo creados exitosamente'))
        self.stdout.write('Sistema listo para pruebas del módulo de producción')
