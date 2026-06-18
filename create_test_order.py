#!/usr/bin/env python
import os
import django
import sys
from django.utils import timezone

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from productos.models import Producto
from produccion.models import OrdenProduccion

def create_test_order_in_progress():
    print("🧪 Creando orden de producción en progreso para probar el botón 'Completar'...")

    # Obtener usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No hay usuario admin")
        return

    # Obtener un producto con receta
    producto = Producto.objects.filter(receta__isnull=False).first()
    if not producto:
        print("❌ No hay productos con receta")
        return

    print(f"📦 Producto seleccionado: {producto.nombre}")

    # Crear orden de producción en estado 'en_progreso'
    try:
        orden = OrdenProduccion.objects.create(
            producto=producto,
            receta=producto.receta,
            cantidad_a_producir=2,
            estado='en_progreso',
            responsable=admin_user,
            fecha_inicio=timezone.now()
        )

        # Consumir las materias primas (simular que ya se inició)
        orden.consumir_materias_primas()

        print(f"✅ Orden de producción creada en estado 'En Progreso': OP-{orden.id}")
        print(f"   - Producto: {orden.producto.nombre}")
        print(f"   - Cantidad: {orden.cantidad_a_producir}")
        print(f"   - Estado: {orden.get_estado_display()}")
        print(f"   - Materias primas consumidas: ✅")

        print("\n🎯 Ahora puedes ir a la lista de órdenes de producción y hacer clic en 'Completar'")
        print("   URL: http://127.0.0.1:8000/produccion/")
        print(f"   Busca la orden OP-{orden.id}")

    except Exception as e:
        print(f"❌ Error al crear orden: {e}")

if __name__ == '__main__':
    create_test_order_in_progress()