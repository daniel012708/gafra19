#!/usr/bin/env python
import os
import django
import sys
from decimal import Decimal
from django.utils import timezone

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from productos.models import Producto, Categoria, Receta, IngredienteReceta
from proveedores.models import Proveedor
from clientes.models import Cliente
from ventas.models import Venta, DetalleVenta, Carrito, ItemCarrito
from inventario.models import MateriaPrima, MovimientoMateriaPrima
from produccion.models import OrdenProduccion, ProduccionDiaria
from faker import Faker
import random

fake = Faker('es_ES')

def clear_all_data():
    """Borra todos los datos existentes"""
    print("🗑️ Borrando todos los datos existentes...")

    # Borrar en orden inverso de dependencias
    ProduccionDiaria.objects.all().delete()
    OrdenProduccion.objects.all().delete()
    ItemCarrito.objects.all().delete()
    Carrito.objects.all().delete()
    DetalleVenta.objects.all().delete()
    Venta.objects.all().delete()
    Receta.objects.all().delete()
    IngredienteReceta.objects.all().delete()
    Producto.objects.all().delete()
    Categoria.objects.all().delete()
    MovimientoMateriaPrima.objects.all().delete()
    MateriaPrima.objects.all().delete()
    Cliente.objects.all().delete()
    Proveedor.objects.all().delete()

    print("✅ Todos los datos borrados")

def create_categories():
    """Crear categorías"""
    print("📂 Creando categorías...")
    categories = [
        {'nombre': 'Cunas', 'descripcion': 'Cunas para bebés'},
        {'nombre': 'Sillas', 'descripcion': 'Sillas altas y de comer'},
        {'nombre': 'Ropa', 'descripcion': 'Ropa para bebés'},
    ]

    created_categories = {}
    for cat_data in categories:
        cat, created = Categoria.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion']}
        )
        created_categories[cat_data['nombre']] = cat
        if created:
            print(f"  ✅ {cat.nombre}")

    return created_categories

def create_suppliers():
    """Crear 20 proveedores"""
    print("🏭 Creando 20 proveedores...")
    suppliers = []
    for i in range(20):
        supplier, created = Proveedor.objects.get_or_create(
            nombre=fake.company(),
            defaults={
                'contacto': fake.name(),
                'telefono': fake.phone_number(),
                'email': fake.email(),
                'direccion': fake.address().replace('\n', ', ')
            }
        )
        suppliers.append(supplier)
        if created:
            print(f"  ✅ {supplier.nombre}")

    return suppliers

def create_materials(suppliers):
    """Crear materias primas"""
    print("🔧 Creando materias primas...")

    materials_data = [
        ('Madera', 'kg', 50),
        ('Metal', 'kg', 80),
        ('Tela', 'm²', 30),
        ('Plástico', 'kg', 40),
        ('Espuma', 'kg', 25),
        ('Algodón', 'kg', 60),
        ('Poliéster', 'kg', 45),
        ('Tornillos', 'unidad', 200),
        ('Pegamento', 'kg', 35),
        ('Pintura', 'litro', 55),
        ('Goma', 'kg', 30),
        ('Cuero', 'm²', 90),
        ('Vidrio', 'm²', 70),
        ('Caucho', 'kg', 40),
        ('Barniz', 'litro', 65),
        ('Tintes', 'kg', 100),
        ('Sellador', 'kg', 50),
        ('Lubricante', 'litro', 85),
        ('Remaches', 'unidad', 150),
        ('Pintura', 'litro', 55),
    ]

    materials = {}
    for name, unit, price in materials_data:
        material, created = MateriaPrima.objects.get_or_create(
            nombre=name,
            proveedor=random.choice(suppliers),
            defaults={
                'descripcion': f'Materia prima: {name}',
                'precio_unitario': Decimal(str(price)),
                'unidad_medida': unit,
                'stock_actual': Decimal(str(random.randint(500, 2000))),
                'stock_minimo': Decimal(str(random.randint(50, 200))),
                'activo': True
            }
        )
        materials[name] = material
        if created:
            print(f"  ✅ {material.nombre} - Stock: {material.stock_actual} {material.unidad_medida}")

    return materials

def create_products(categories, suppliers):
    """Crear los 3 productos principales con 20 unidades cada uno"""
    print("📦 Creando productos...")

    products_data = [
        {
            'codigo': 'CUN001',
            'nombre': 'Cuna Blanca Moderna',
            'descripcion': 'Cuna blanca con diseño moderno, perfecta para el cuarto del bebé. Incluye colchón y sábanas.',
            'precio_costo': Decimal('150.00'),
            'precio_venta': Decimal('250.00'),
            'categoria': categories['Cunas'],
            'stock_actual': 20
        },
        {
            'codigo': 'SIL001',
            'nombre': 'Silla Alta Azul',
            'descripcion': 'Silla alta azul con bandeja extraíble y sistema de seguridad. Ideal para la hora de comer.',
            'precio_costo': Decimal('80.00'),
            'precio_venta': Decimal('140.00'),
            'categoria': categories['Sillas'],
            'stock_actual': 20
        },
        {
            'codigo': 'ROP001',
            'nombre': 'Body Rosa para Bebé',
            'descripcion': 'Body rosa de algodón suave, talla 3-6 meses. Perfecto para el día a día.',
            'precio_costo': Decimal('15.00'),
            'precio_venta': Decimal('35.00'),
            'categoria': categories['Ropa'],
            'stock_actual': 20
        }
    ]

    products = {}
    for prod_data in products_data:
        product, created = Producto.objects.get_or_create(
            codigo=prod_data['codigo'],
            defaults={
                'nombre': prod_data['nombre'],
                'descripcion': prod_data['descripcion'],
                'categoria': prod_data['categoria'],
                'precio_costo': prod_data['precio_costo'],
                'precio_venta': prod_data['precio_venta'],
                'stock_actual': prod_data['stock_actual'],
                'activo': True
            }
        )
        products[prod_data['codigo']] = product
        if created:
            print(f"  ✅ {product.nombre} - Stock: {product.stock_actual}")

    return products

def create_recipes(products, materials):
    """Crear recetas para los productos"""
    print("📋 Creando recetas...")

    recipes_data = {
        'CUN001': {  # Cuna Blanca Moderna
            'descripcion': 'Receta para cuna blanca moderna',
            'tiempo_produccion': 180,  # 3 horas
            'ingredientes': {
                'Madera': Decimal('15.0'),  # kg de madera
                'Metal': Decimal('5.0'),   # kg de metal para estructura
                'Tornillos': Decimal('50.0'),  # unidades
                'Pegamento': Decimal('2.0'),   # kg
                'Pintura': Decimal('1.5'),    # litros
            }
        },
        'SIL001': {  # Silla Alta Azul
            'descripcion': 'Receta para silla alta azul',
            'tiempo_produccion': 90,   # 1.5 horas
            'ingredientes': {
                'Plástico': Decimal('8.0'),   # kg de plástico
                'Metal': Decimal('3.0'),     # kg de metal
                'Espuma': Decimal('2.0'),    # kg de espuma
                'Tela': Decimal('1.5'),      # m² de tela
                'Tornillos': Decimal('25.0'), # unidades
                'Pegamento': Decimal('1.0'),  # kg
            }
        },
        'ROP001': {  # Body Rosa para Bebé
            'descripcion': 'Receta para body rosa de algodón',
            'tiempo_produccion': 45,   # 45 minutos
            'ingredientes': {
                'Algodón': Decimal('0.3'),   # kg de algodón
                'Poliéster': Decimal('0.1'), # kg de poliéster
                'Tintes': Decimal('0.05'),   # kg de tintes
            }
        }
    }

    for codigo, recipe_data in recipes_data.items():
        product = products[codigo]

        # Crear receta
        receta, created = Receta.objects.get_or_create(
            producto=product,
            defaults={
                'descripcion': recipe_data['descripcion'],
                'tiempo_produccion': recipe_data['tiempo_produccion'],
                'activo': True
            }
        )

        if created:
            print(f"  ✅ Receta para {product.nombre}")

            # Agregar ingredientes
            for nombre_mp, cantidad in recipe_data['ingredientes'].items():
                if nombre_mp in materials:
                    IngredienteReceta.objects.create(
                        receta=receta,
                        materia_prima=materials[nombre_mp],
                        cantidad_requerida=cantidad
                    )
                    print(f"    - {nombre_mp}: {cantidad} {materials[nombre_mp].unidad_medida}")

def create_clients():
    """Crear 20 clientes"""
    print("👥 Creando 20 clientes...")
    clients = []
    for i in range(20):
        client, created = Cliente.objects.get_or_create(
            nombre=fake.name(),
            defaults={
                'email': fake.email(),
                'telefono': fake.phone_number(),
                'direccion': fake.address().replace('\n', ', '),
                'documento': fake.ssn()
            }
        )
        clients.append(client)
        if created:
            print(f"  ✅ {client.nombre}")

    return clients

def create_orders(products, clients):
    """Crear 20 órdenes de producción en diferentes estados"""
    print("🏭 Creando órdenes de producción...")
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario admin")
        return

    orders = []
    estados = ['pendiente', 'en_progreso', 'completada']

    for i in range(20):
        product = random.choice(list(products.values()))
        estado = random.choice(estados)

        order = OrdenProduccion.objects.create(
            producto=product,
            receta=product.receta,
            cantidad_a_producir=random.randint(1, 10),
            estado=estado,
            responsable=admin_user,
            fecha_inicio=timezone.now() if estado in ['en_progreso', 'completada'] else None,
            fecha_fin=timezone.now() if estado == 'completada' else None,
            notas=fake.sentence()
        )

        # Si está en progreso o completada, consumir materias primas
        if estado in ['en_progreso', 'completada']:
            order.consumir_materias_primas()

        # Si está completada, producir productos
        if estado == 'completada':
            order.producir_productos()

            # Crear registro de producción diaria
            ProduccionDiaria.objects.create(
                orden_produccion=order,
                fecha=timezone.now().date(),
                cantidad_producida=order.cantidad_a_producir,
                tiempo_trabajado=random.randint(60, 480),  # 1-8 horas
                observaciones=f"Producción completada exitosamente",
                responsable=admin_user
            )

        orders.append(order)
        print(f"  ✅ OP-{order.id} - {product.nombre} ({estado})")

    return orders

def create_sales(products, clients):
    """Crear 20 ventas"""
    print("🛒 Creando 20 ventas...")

    sales = []
    estados_venta = ['pendiente', 'completada']

    for i in range(20):
        client = random.choice(clients)
        estado = random.choice(estados_venta)

        # Crear venta
        venta = Venta.objects.create(
            vendedor=User.objects.filter(is_superuser=True).first(),
            cliente=client,
            estado=estado,
            descuento=Decimal('0.00'),
            impuesto=Decimal('0.00'),
            total=Decimal('0.00'),
            observaciones=fake.sentence() if random.choice([True, False]) else ''
        )

        # Agregar productos a la venta
        total_venta = Decimal('0.00')
        num_items = random.randint(1, 5)

        for _ in range(num_items):
            product = random.choice(list(products.values()))
            cantidad = random.randint(1, 3)
            precio_unitario = product.precio_venta
            subtotal = precio_unitario * cantidad

            DetalleVenta.objects.create(
                venta=venta,
                producto=product,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )

            total_venta += subtotal

            # Reducir stock si la venta está completada
            if estado == 'completada':
                product.stock_actual -= cantidad
                product.save()

        # Actualizar total de la venta
        venta.total = total_venta
        venta.save()

        sales.append(venta)
        print(f"  ✅ Venta {venta.numero_venta} - {client.nombre} - ${total_venta} ({estado})")

    return sales

def main():
    print("🚀 Iniciando recreación completa de datos...")
    print("=" * 50)

    # Borrar todo
    clear_all_data()
    print()

    # Crear datos base
    categories = create_categories()
    print()

    suppliers = create_suppliers()
    print()

    materials = create_materials(suppliers)
    print()

    products = create_products(categories, suppliers)
    print()

    create_recipes(products, materials)
    print()

    clients = create_clients()
    print()

    # Crear órdenes de producción
    orders = create_orders(products, clients)
    print()

    # Crear ventas
    sales = create_sales(products, clients)
    print()

    print("=" * 50)
    print("✅ Recreación completa finalizada!")
    print()
    print("📊 Resumen:")
    print(f"  • Categorías: {Categoria.objects.count()}")
    print(f"  • Proveedores: {Proveedor.objects.count()}")
    print(f"  • Materias Primas: {MateriaPrima.objects.count()}")
    print(f"  • Productos: {Producto.objects.count()}")
    print(f"  • Recetas: {Receta.objects.count()}")
    print(f"  • Clientes: {Cliente.objects.count()}")
    print(f"  • Órdenes de Producción: {OrdenProduccion.objects.count()}")
    print(f"  • Ventas: {Venta.objects.count()}")
    print()
    print("🎯 Los 3 productos principales:")
    for codigo, product in products.items():
        print(f"  • {product.nombre}: {product.stock_actual} unidades")

if __name__ == '__main__':
    main()