#!/usr/bin/env python
"""
Script para crear datos de prueba realistas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')
django.setup()

from django.contrib.auth.models import User
from usuario.models import Usuario
from productos.models import Producto, Categoria, Receta, IngredienteReceta
from proveedores.models import Proveedor
from clientes.models import Cliente
from inventario.models import MateriaPrima
from produccion.models import OrdenProduccion
from decimal import Decimal
import random
from faker import Faker

fake = Faker('es_ES')

print("🚀 Creando datos de prueba...")

# Crear categorías
print("\n📦 Creando categorías...")
categorias_data = [
    {'nombre': 'Muebles para Bebé', 'descripcion': 'Muebles especializados para bebés'},
    {'nombre': 'Accesorios', 'descripcion': 'Accesorios varios para el hogar'},
]
categorias = {}
for cat_data in categorias_data:
    cat, created = Categoria.objects.get_or_create(
        nombre=cat_data['nombre'],
        defaults={'descripcion': cat_data['descripcion']}
    )
    categorias[cat_data['nombre']] = cat
    print(f"  ✓ {cat.nombre}")

# Crear productos (3 tipos con variaciones de color)
print("\n🛒 Creando productos...")
categoria_muebles = categorias['Muebles para Bebé']

productos_base = [
    {
        'codigo': 'COCHE-001',
        'nombre': 'Coche de Bebé',
        'descripcion': 'Coche de bebé cómodo y seguro con excelentes características',
        'colores': ['Negro', 'Gris', 'Beige', 'Azul']
    },
    {
        'codigo': 'CUNA-001',
        'nombre': 'Cuna de Bebé',
        'descripcion': 'Cuna de madera de alta calidad con sistema de seguridad avanzado',
        'colores': ['Blanco', 'Roble', 'Nogal', 'Pino']
    },
    {
        'codigo': 'MECE-001',
        'nombre': 'Mecedora',
        'descripcion': 'Mecedora ergonómica perfecta para alimentar a tu bebé',
        'colores': ['Blanco', 'Gris', 'Marrón', 'Rosa']
    }
]

productos_ids = []
for prod_base in productos_base:
    for idx, color in enumerate(prod_base['colores'], 1):
        codigo = f"{prod_base['codigo'].split('-')[0]}-{color.upper()[:3]}-{idx:03d}"
        nombre = f"{prod_base['nombre']} - {color}"
        
        prod, created = Producto.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': prod_base['descripcion'],
                'categoria': categoria_muebles,
                'precio_costo': Decimal(str(random.randint(800, 1500))),
                'precio_venta': Decimal(str(random.randint(1500, 3000))),
                'stock_actual': random.randint(5, 50),
                'activo': True,
            }
        )
        if created:
            print(f"  ✓ {nombre}")
        productos_ids.append(prod.id)

# Crear proveedores
print("\n🏭 Creando proveedores...")
for _ in range(20):
    empresa = fake.company()
    Proveedor.objects.get_or_create(
        nombre=empresa,
        defaults={
            'contacto': fake.name(),
            'email': fake.email(),
            'telefono': fake.phone_number(),
            'direccion': fake.address(),
        }
    )
print(f"  ✓ 20 proveedores creados")

# Crear clientes
print("\n👥 Creando clientes...")
for _ in range(20):
    Cliente.objects.get_or_create(
        email=fake.email(),
        defaults={
            'nombre': fake.name(),
            'documento': fake.ssn(),
            'telefono': fake.phone_number(),
            'direccion': fake.address(),
        }
    )
print(f"  ✓ 20 clientes creados")

# Crear materias primas
print("\n📋 Creando materias primas...")
materias_primas = [
    'Acero', 'Madera', 'Tela', 'Plástico', 'Espuma', 'Cuero',
    'Algodón', 'Poliéster', 'Goma', 'Pintura', 'Barniz', 'Tornillos',
    'Remaches', 'Pegamento', 'Tintes', 'Sellador', 'Lubricante', 'Metal',
    'Vidrio', 'Caucho'
]
proveedores = list(Proveedor.objects.all()[:20])
for idx, materia in enumerate(materias_primas):
    MateriaPrima.objects.get_or_create(
        nombre=materia,
        proveedor=proveedores[idx % len(proveedores)],
        defaults={
            'descripcion': f'Materia prima: {materia}',
            'stock_actual': random.randint(100, 1000),
            'stock_minimo': random.randint(10, 50),
            'unidad_medida': 'kg' if materia in ['Acero', 'Madera', 'Tela', 'Plástico'] else 'unidad',
            'precio_unitario': Decimal(str(random.randint(10, 1000))),
        }
    )
print(f"  ✓ {len(materias_primas)} materias primas creadas")

# Crear órdenes de producción
print("\n⚙️ Creando órdenes de producción...")
estados = ['pendiente', 'en_progreso', 'completada', 'cancelada']

# Primero crear recetas para los productos
for producto in Producto.objects.all()[:3]:
    receta, _ = Receta.objects.get_or_create(
        producto=producto,
        defaults={'descripcion': f'Receta para {producto.nombre}', 'tiempo_produccion': 120}
    )
    # Agregar algunos ingredientes
    materias = MateriaPrima.objects.all()[:3]
    for materia in materias:
        IngredienteReceta.objects.get_or_create(
            receta=receta,
            materia_prima=materia,
            defaults={'cantidad_requerida': Decimal(str(random.uniform(0.5, 5)))}
        )

# Ahora crear órdenes de producción
for _ in range(20):
    producto = Producto.objects.order_by('?').first()
    receta = Receta.objects.filter(producto=producto).first()
    
    if receta:
        OrdenProduccion.objects.get_or_create(
            producto=producto,
            receta=receta,
            cantidad_a_producir=random.randint(1, 20),
            defaults={
                'estado': random.choice(estados),
                'notas': fake.paragraph(),
            }
        )
print(f"  ✓ 20 órdenes de producción creadas")

print("\n✅ ¡Datos de prueba creados exitosamente!")
