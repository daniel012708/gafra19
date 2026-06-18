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
    help = 'Populate sample data for baby products business'

    def handle(self, *args, **options):
        # Create a user
        user, _ = User.objects.get_or_create(username='sampleadmin', defaults={'email': 'admin@local'})

        # Proveedores
        provs = []
        proveedores_data = [
            ('Maderas del Valle', 'Proveedor de maderas para muebles'),
            ('Plásticos Industriales', 'Fabricante de componentes plásticos'),
            ('Metales y Aleaciones', 'Suministrador de piezas metálicas'),
            ('Telas y Tejidos', 'Proveedor de telas y acolchados'),
            ('Espumas y Rellenos', 'Especialista en espumas y acolchados'),
        ]

        for nombre, desc in proveedores_data:
            p, _ = Proveedor.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'contacto': f'Contacto de {nombre}',
                    'telefono': f'300000000{random.randint(1,9)}',
                    'email': f'contacto@{nombre.lower().replace(" ", "")}.com',
                    'direccion': f'Dirección de {nombre}',
                    'ciudad': 'Bogotá',
                    'pais': 'Colombia'
                }
            )
            provs.append(p)

        # Categorías
        cats = []
        categorias_data = ['Muebles Infantiles', 'Accesorios para Bebés', 'Seguridad Infantil', 'Transporte']
        for nombre in categorias_data:
            c, _ = Categoria.objects.get_or_create(nombre=nombre)
            cats.append(c)

        # Materias Primas
        materias = []
        materias_data = [
            ('Madera Pino', 'Madera de pino tratada para muebles', 'M3', 500, 100, 15000),
            ('Madera Roble', 'Madera de roble para estructuras', 'M3', 300, 50, 25000),
            ('Plástico ABS', 'Plástico ABS resistente', 'KG', 200, 40, 8000),
            ('Acero Inoxidable', 'Acero inoxidable para piezas', 'KG', 150, 30, 12000),
            ('Aluminio', 'Aluminio para marcos ligeros', 'KG', 100, 20, 18000),
            ('Tela Algodón', 'Tela de algodón suave', 'M2', 400, 80, 5000),
            ('Espuma Viscoelástica', 'Espuma de alta densidad', 'KG', 80, 15, 35000),
            ('Pintura Blanca', 'Pintura no tóxica blanca', 'L', 50, 10, 25000),
            ('Pintura Azul', 'Pintura no tóxica azul', 'L', 30, 8, 25000),
            ('Pintura Rosa', 'Pintura no tóxica rosa', 'L', 25, 8, 25000),
            ('Ruedas de Goma', 'Ruedas con suspensión', 'UNIDAD', 200, 40, 5000),
            ('Bisagras Metálicas', 'Bisagras resistentes', 'UNIDAD', 300, 60, 2000),
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

        # Productos con variantes y recetas
        productos_data = [
            # Corrales
            ('Corral Portátil Blanco', 'Corral plegable con base blanca', 'Seguridad Infantil', [
                ('Madera Pino', 0.5), ('Tela Algodón', 2), ('Plástico ABS', 1), ('Bisagras Metálicas', 4), ('Pintura Blanca', 0.5)
            ]),
            ('Corral Portátil Azul', 'Corral plegable con base azul', 'Seguridad Infantil', [
                ('Madera Pino', 0.5), ('Tela Algodón', 2), ('Plástico ABS', 1), ('Bisagras Metálicas', 4), ('Pintura Azul', 0.5)
            ]),
            ('Corral Portátil Rosa', 'Corral plegable con base rosa', 'Seguridad Infantil', [
                ('Madera Pino', 0.5), ('Tela Algodón', 2), ('Plástico ABS', 1), ('Bisagras Metálicas', 4), ('Pintura Rosa', 0.5)
            ]),

            # Cunas
            ('Cuna Bebé Blanca', 'Cuna tradicional blanca con barandas', 'Muebles Infantiles', [
                ('Madera Roble', 1.2), ('Tela Algodón', 1.5), ('Espuma Viscoelástica', 2), ('Bisagras Metálicas', 2), ('Pintura Blanca', 0.8)
            ]),
            ('Cuna Bebé Azul', 'Cuna tradicional azul con barandas', 'Muebles Infantiles', [
                ('Madera Roble', 1.2), ('Tela Algodón', 1.5), ('Espuma Viscoelástica', 2), ('Bisagras Metálicas', 2), ('Pintura Azul', 0.8)
            ]),
            ('Cuna Bebé Rosa', 'Cuna tradicional rosa con barandas', 'Muebles Infantiles', [
                ('Madera Roble', 1.2), ('Tela Algodón', 1.5), ('Espuma Viscoelástica', 2), ('Bisagras Metálicas', 2), ('Pintura Rosa', 0.8)
            ]),

            # Coches/Coches de Bebé
            ('Coche Bebé Plegable Azul', 'Coche plegable con capota azul', 'Transporte', [
                ('Aluminio', 3), ('Plástico ABS', 2), ('Tela Algodón', 1.5), ('Ruedas de Goma', 4), ('Pintura Azul', 0.3)
            ]),
            ('Coche Bebé Plegable Rosa', 'Coche plegable con capota rosa', 'Transporte', [
                ('Aluminio', 3), ('Plástico ABS', 2), ('Tela Algodón', 1.5), ('Ruedas de Goma', 4), ('Pintura Rosa', 0.3)
            ]),
            ('Coche Bebé Plegable Blanco', 'Coche plegable con capota blanca', 'Transporte', [
                ('Aluminio', 3), ('Plástico ABS', 2), ('Tela Algodón', 1.5), ('Ruedas de Goma', 4), ('Pintura Blanca', 0.3)
            ]),

            # Accesorios adicionales
            ('Almohada para Cuna', 'Almohada suave para cunas', 'Accesorios para Bebés', [
                ('Tela Algodón', 0.5), ('Espuma Viscoelástica', 0.3)
            ]),
            ('Mosquitero para Cuna', 'Mosquitero protector para cunas', 'Accesorios para Bebés', [
                ('Tela Algodón', 1), ('Plástico ABS', 0.1)
            ]),
            ('Bolsa Organizadora', 'Bolsa organizadora para coche', 'Accesorios para Bebés', [
                ('Tela Algodón', 0.8), ('Plástico ABS', 0.2)
            ]),
        ]

        prods = []
        for i, (nombre, desc, cat_nombre, ingredientes) in enumerate(productos_data, 1):
            categoria = Categoria.objects.get(nombre=cat_nombre)
            prod, _ = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'codigo': f'BB{i:03d}',
                    'descripcion': desc,
                    'categoria': categoria,
                    'precio_costo': random.randint(50000, 200000),
                    'precio_venta': random.randint(80000, 350000),
                    'stock_actual': random.randint(0, 20),
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
        nombres_clientes = ['María González', 'Carlos Rodríguez', 'Ana López', 'Juan Martínez', 'Laura Sánchez',
                           'Pedro Ramírez', 'Sofia Torres', 'Diego Morales', 'Valentina Castro', 'Andrés Herrera',
                           'Camila Jiménez', 'Felipe Vargas', 'Isabella Ruiz', 'Mateo Silva', 'Lucía Mendoza',
                           'Sebastián Ortega', 'Emma Delgado', 'Lucas Guzmán', 'Victoria Peña', 'Daniel Rojas']

        for i, nombre in enumerate(nombres_clientes, 1):
            c, _ = Cliente.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'documento': f'1{random.randint(10000000, 99999999)}',
                    'direccion': f'Calle {random.randint(1,100)} #{random.randint(1,50)}-45',
                    'telefono': f'3{random.randint(100000000, 999999999)}',
                    'email': f'{nombre.lower().replace(" ", ".")}@example.com'
                }
            )
            clients.append(c)

        # Órdenes de producción de ejemplo
        for prod in prods[:10]:  # Para varios productos
            if hasattr(prod, 'receta') and prod.receta.activo:
                orden = OrdenProduccion.objects.create(
                    producto=prod,
                    receta=prod.receta,
                    cantidad_a_producir=random.randint(5, 25),
                    responsable=user,
                    estado='PENDIENTE'
                )
                self.stdout.write(f'Orden de producción creada: {orden}')

        # Ventas de ejemplo
        for i in range(1, 21):
            v = Venta.objects.create(
                vendedor=user,
                cliente=random.choice(clients),
                estado='completada',
                descuento=random.randint(0, 50000),
                impuesto=0,
                total=0  # Valor temporal, se recalculará
            )
            # Detalles de venta
            for _ in range(random.randint(1, 4)):
                prod = random.choice(prods)
                cantidad = random.randint(1, 3)
                precio = prod.precio_venta
                subtotal = cantidad * precio
                DetalleVenta.objects.create(
                    venta=v,
                    producto=prod,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal
                )

            # Recalcular el total después de agregar detalles
            v.recompute_total()
            v.total = sum(d.cantidad * d.precio_unitario for d in v.detalles.all()) - v.descuento + v.impuesto
            v.save()

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo para productos de bebés creados exitosamente'))
        self.stdout.write('Sistema listo para pruebas del módulo de producción con productos infantiles')