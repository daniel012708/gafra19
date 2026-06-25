#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')
django.setup()

from clientes.models import Cliente
from ventas.models import Venta
from productos.models import Producto
from django.contrib.auth.models import User
from decimal import Decimal

# Restaurar el cliente
cliente = Cliente.objects.all_including_deleted().first()
cliente.restore()
print(f"✓ Cliente restaurado: {cliente.nombre}")

# Crear un producto
usuario = User.objects.first()
producto = Producto.objects.create(
    nombre="Producto Test",
    descripcion="Test",
    precio_venta=Decimal('100.00')
)
print(f"✓ Producto creado: {producto.nombre}")

# Crear una venta
venta = Venta.objects.create(
    cliente=cliente,
    vendedor=usuario,
    total=Decimal('100.00')
)
print(f"✓ Venta creada: {venta.numero_venta}, Cliente: {venta.cliente.nombre}")

# Ahora eliminar el cliente
cliente.delete()
print(f"\n✓ Cliente eliminado: {cliente.nombre}, Deleted: {cliente.deleted}")

# Verificar que la venta sigue referenciando al cliente
venta.refresh_from_db()
print(f"✓ Venta después de eliminar cliente: {venta.numero_venta}")
print(f"✓ Cliente de la venta: {venta.cliente.nombre}")
print(f"✓ Estado del cliente: Deleted={venta.cliente.deleted}")
print("\n✅ SOFT DELETE FUNCIONA: Los datos relacionados permanecen intactos")
