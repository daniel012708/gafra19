#!/usr/bin/env python
import os
import django
import sys
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')

# Setup Django
django.setup()

from productos.models import Producto, Categoria
from proveedores.models import Proveedor

# Create categories if they don't exist
categories_data = [
    {'nombre': 'Cunas', 'descripcion': 'Cunas para bebés'},
    {'nombre': 'Sillas', 'descripcion': 'Sillas altas y de comer'},
    {'nombre': 'Ropa', 'descripcion': 'Ropa para bebés'},
    {'nombre': 'Juguetes', 'descripcion': 'Juguetes educativos'},
    {'nombre': 'Accesorios', 'descripcion': 'Accesorios varios'},
]

categories = {}
for cat_data in categories_data:
    cat, created = Categoria.objects.get_or_create(
        nombre=cat_data['nombre'],
        defaults={'descripcion': cat_data['descripcion']}
    )
    categories[cat_data['nombre']] = cat
    if created:
        print(f'Created category: {cat.nombre}')

# Create a supplier if it doesn't exist
supplier, created = Proveedor.objects.get_or_create(
    nombre='Proveedor Demo',
    defaults={
        'contacto': 'Juan Pérez',
        'telefono': '123456789',
        'email': 'proveedor@demo.com',
        'direccion': 'Calle Demo 123'
    }
)
if created:
    print('Created supplier: Proveedor Demo')

# Create sample products
products_data = [
    {
        'codigo': 'CUN001',
        'nombre': 'Cuna Blanca Moderna',
        'descripcion': 'Cuna blanca con diseño moderno, perfecta para el cuarto del bebé. Incluye colchón y sábanas.',
        'precio_costo': Decimal('150.00'),
        'precio_venta': Decimal('250.00'),
        'stock_actual': 15,
        'categoria': categories['Cunas'],
        'activo': True
    },
    {
        'codigo': 'SIL001',
        'nombre': 'Silla Alta Azul',
        'descripcion': 'Silla alta azul con bandeja extraíble y sistema de seguridad. Ideal para la hora de comer.',
        'precio_costo': Decimal('80.00'),
        'precio_venta': Decimal('140.00'),
        'stock_actual': 20,
        'categoria': categories['Sillas'],
        'activo': True
    },
    {
        'codigo': 'ROP001',
        'nombre': 'Body Rosa para Bebé',
        'descripcion': 'Body rosa de algodón suave, talla 3-6 meses. Perfecto para el día a día.',
        'precio_costo': Decimal('15.00'),
        'precio_venta': Decimal('35.00'),
        'stock_actual': 50,
        'categoria': categories['Ropa'],
        'activo': True
    },
    {
        'codigo': 'JUG001',
        'nombre': 'Juguete Educativo Multicolor',
        'descripcion': 'Juguete educativo con sonidos y colores vibrantes. Ayuda al desarrollo cognitivo.',
        'precio_costo': Decimal('25.00'),
        'precio_venta': Decimal('55.00'),
        'stock_actual': 30,
        'categoria': categories['Juguetes'],
        'activo': True
    },
    {
        'codigo': 'ACC001',
        'nombre': 'Set de Baño para Bebé',
        'descripcion': 'Set completo de baño con toalla, jabón y esponja. Todo lo necesario para el baño diario.',
        'precio_costo': Decimal('30.00'),
        'precio_venta': Decimal('65.00'),
        'stock_actual': 25,
        'categoria': categories['Accesorios'],
        'activo': True
    },
    {
        'codigo': 'CUN002',
        'nombre': 'Cuna de Madera Natural',
        'descripcion': 'Cuna de madera natural con acabados suaves. Diseño clásico y duradero.',
        'precio_costo': Decimal('200.00'),
        'precio_venta': Decimal('350.00'),
        'stock_actual': 8,
        'categoria': categories['Cunas'],
        'activo': True
    },
    {
        'codigo': 'SIL002',
        'nombre': 'Silla Mecedora Verde',
        'descripcion': 'Silla mecedora verde suave para bebés. Perfecta para relajarse y dormir.',
        'precio_costo': Decimal('120.00'),
        'precio_venta': Decimal('200.00'),
        'stock_actual': 12,
        'categoria': categories['Sillas'],
        'activo': True
    },
    {
        'codigo': 'ROP002',
        'nombre': 'Pijama Azul con Estrellas',
        'descripcion': 'Pijama azul con estampado de estrellas, talla 6-12 meses. Cómodo y adorable.',
        'precio_costo': Decimal('20.00'),
        'precio_venta': Decimal('45.00'),
        'stock_actual': 40,
        'categoria': categories['Ropa'],
        'activo': True
    }
]

created_count = 0
for product_data in products_data:
    product, created = Producto.objects.get_or_create(
        codigo=product_data['codigo'],
        defaults=product_data
    )
    if created:
        created_count += 1
        print(f'Created product: {product.nombre}')

print(f'\nSummary: Created {created_count} new products')
print(f'Total products in database: {Producto.objects.count()}')