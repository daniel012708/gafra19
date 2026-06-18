import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')

import django

django.setup()

from usuario.models import Usuario
from clientes.models import Cliente
from proveedores.models import Proveedor
from inventario.models import MateriaPrima
from productos.models import Producto
from produccion.models import OrdenProduccion, ProduccionDiaria
from ventas.models import Venta, DetalleVenta

print({
    'admins': Usuario.objects.filter(rol='admin').count(),
    'clientes_role': Usuario.objects.filter(rol='cliente').count(),
    'logistica': Usuario.objects.filter(rol='logistica').count(),
    'clientes': Cliente.objects.count(),
    'proveedores': Proveedor.objects.count(),
    'materias': MateriaPrima.objects.count(),
    'productos': Producto.objects.count(),
    'ordenes': OrdenProduccion.objects.count(),
    'produccion_diaria': ProduccionDiaria.objects.count(),
    'ventas': Venta.objects.count(),
    'detalles': DetalleVenta.objects.count(),
})
