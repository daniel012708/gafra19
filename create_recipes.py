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

from productos.models import Producto, Receta, IngredienteReceta
from inventario.models import MateriaPrima
from proveedores.models import Proveedor

def create_recipes():
    print("Creando recetas para productos...")

    # Obtener productos existentes
    productos = {
        'CUN001': Producto.objects.filter(codigo='CUN001').first(),
        'SIL001': Producto.objects.filter(codigo='SIL001').first(),
        'ROP001': Producto.objects.filter(codigo='ROP001').first(),
    }

    # Obtener materias primas comunes
    materias_primas = {}
    nombres_mp = ['Madera', 'Metal', 'Tela', 'Plástico', 'Espuma', 'Algodón', 'Poliéster', 'Tornillos', 'Pegamento', 'Pintura']

    for nombre in nombres_mp:
        mp = MateriaPrima.objects.filter(nombre=nombre).first()
        if mp:
            materias_primas[nombre] = mp
        else:
            print(f"Materia prima '{nombre}' no encontrada")

    # Recetas para cada producto
    recetas_data = {
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

    for codigo, receta_data in recetas_data.items():
        producto = productos[codigo]
        if not producto:
            print(f"Producto {codigo} no encontrado, saltando...")
            continue

        # Crear o actualizar receta
        receta, created = Receta.objects.get_or_create(
            producto=producto,
            defaults={
                'descripcion': receta_data['descripcion'],
                'tiempo_produccion': receta_data['tiempo_produccion'],
                'activo': True
            }
        )

        if created:
            print(f"Receta creada para {producto.nombre}")
        else:
            print(f"Receta actualizada para {producto.nombre}")
            # Limpiar ingredientes existentes
            receta.ingredientes.all().delete()

        # Agregar ingredientes
        for nombre_mp, cantidad in receta_data['ingredientes'].items():
            if nombre_mp in materias_primas:
                IngredienteReceta.objects.create(
                    receta=receta,
                    materia_prima=materias_primas[nombre_mp],
                    cantidad_requerida=cantidad
                )
                print(f"  - {nombre_mp}: {cantidad} {materias_primas[nombre_mp].unidad_medida}")
            else:
                print(f"  - Materia prima {nombre_mp} no encontrada")

    print("\nRecetas creadas exitosamente!")
    print("\nResumen de consumo aproximado por producto:")
    print("• Cuna Blanca Moderna: 15kg madera, 5kg metal, 50 tornillos, 2kg pegamento, 1.5L pintura")
    print("• Silla Alta Azul: 8kg plástico, 3kg metal, 2kg espuma, 1.5m² tela, 25 tornillos")
    print("• Body Rosa: 0.3kg algodón, 0.1kg poliéster, 0.05kg tintes")

if __name__ == '__main__':
    create_recipes()