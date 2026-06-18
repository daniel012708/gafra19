#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from productos.models import Producto
from produccion.models import OrdenProduccion

def test_order_creation():
    print("🧪 Probando creación de orden de producción...")

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
    print(f"📋 Receta: {producto.receta}")

    # Crear orden de producción
    try:
        orden = OrdenProduccion.objects.create(
            producto=producto,
            receta=producto.receta,  # Esto debería asignarse automáticamente
            cantidad_a_producir=3,
            responsable=admin_user
        )
        print(f"✅ Orden de producción creada exitosamente: OP-{orden.id}")
        print(f"   - Producto: {orden.producto.nombre}")
        print(f"   - Receta: {orden.receta}")
        print(f"   - Cantidad: {orden.cantidad_a_producir}")
        print(f"   - Estado: {orden.get_estado_display()}")

        # Verificar que puede iniciar
        puede_iniciar = orden.puede_iniciar()
        print(f"   - Puede iniciar: {'✅ Sí' if puede_iniciar else '❌ No'}")

        # Limpiar la orden de prueba
        orden.delete()
        print("🧹 Orden de prueba eliminada")

    except Exception as e:
        print(f"❌ Error al crear orden: {e}")

    print("🎉 Prueba completada!")

if __name__ == '__main__':
    test_order_creation()