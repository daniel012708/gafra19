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
from productos.models import Producto, Receta
from produccion.models import OrdenProduccion, ProduccionDiaria
from inventario.models import MateriaPrima

def test_production_flow():
    print("🧪 Probando flujo completo de producción...")

    # Obtener usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario admin")
        return

    # Obtener productos con recetas
    productos_con_recetas = Producto.objects.filter(receta__isnull=False)[:3]
    if not productos_con_recetas:
        print("❌ No hay productos con recetas")
        return

    print(f"📦 Productos disponibles para producción: {len(productos_con_recetas)}")

    for producto in productos_con_recetas:
        print(f"\n🏭 Probando producción de: {producto.nombre}")

        # Verificar stock de materias primas antes
        print("📊 Stock de materias primas antes:")
        for ingrediente in producto.receta.ingredientes.all():
            cantidad_necesaria = ingrediente.cantidad_requerida * 5  # Para 5 unidades
            stock_actual = ingrediente.materia_prima.stock_actual
            suficiente = stock_actual >= cantidad_necesaria
            status = "✅" if suficiente else "❌"
            print(f"  {status} {ingrediente.materia_prima.nombre}: {stock_actual} (necesita: {cantidad_necesaria})")

        # Crear orden de producción
        orden = OrdenProduccion.objects.create(
            producto=producto,
            receta=producto.receta,
            cantidad_a_producir=5,
            responsable=admin_user
        )
        print(f"📋 Orden de producción creada: OP-{orden.id}")

        # Verificar si puede iniciarse
        puede_iniciar = orden.puede_iniciar()
        print(f"🚀 Puede iniciar producción: {'✅ Sí' if puede_iniciar else '❌ No'}")

        if puede_iniciar:
            # Iniciar producción (esto consume materias primas)
            orden.estado = 'en_progreso'
            orden.fecha_inicio = timezone.now()
            orden.consumir_materias_primas()
            orden.save()
            print("⚙️ Producción iniciada - Materias primas consumidas")

            # Verificar stock después del consumo
            print("📊 Stock de materias primas después del consumo:")
            for ingrediente in producto.receta.ingredientes.all():
                cantidad_consumida = ingrediente.cantidad_requerida * 5
                stock_actual = ingrediente.materia_prima.stock_actual
                print(f"  📉 {ingrediente.materia_prima.nombre}: {stock_actual} (-{cantidad_consumida})")

            # Completar producción
            stock_antes = producto.stock_actual
            orden.producir_productos()
            orden.estado = 'completada'
            orden.fecha_fin = timezone.now()
            orden.save()
            stock_despues = producto.stock_actual

            print(f"✅ Producción completada!")
            print(f"📦 Stock de producto '{producto.nombre}': {stock_antes} → {stock_despues} (+{stock_despues - stock_antes})")

            # Crear registro de producción diaria
            ProduccionDiaria.objects.create(
                orden_produccion=orden,
                fecha=timezone.now().date(),
                cantidad_producida=5,
                tiempo_trabajado=240,  # 4 horas
                observaciones="Prueba automática del sistema",
                responsable=admin_user
            )
            print("📝 Registro de producción diaria creado")
        else:
            print("❌ No se puede iniciar producción - faltan materias primas")
            orden.delete()  # Limpiar orden no usable

    print("\n🎉 Prueba completada!")

if __name__ == '__main__':
    test_production_flow()