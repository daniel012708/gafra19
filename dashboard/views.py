from django.shortcuts import render, redirect
from proveedores.models import Proveedor
from productos.models import Producto
from inventario.models import MateriaPrima
from produccion.models import OrdenProduccion
from clientes.models import Cliente
from ventas.models import Venta
from ventas.models import DetalleVenta
from django.db.models import Sum, F
from datetime import datetime
from gafra.access import get_user_role


def _last_n_months(n=6):
    today = datetime.today()
    months = []
    for i in range(n-1, -1, -1):
        year = (today.year - ((today.month-1-i)//12))
        month = ((today.month-1-i) % 12) + 1
        months.append((year, month))
    return months


def index(request):
    role = get_user_role(request.user)
    if role == 'cliente':
        return redirect('ventas:catalogo_cliente')
    if role == 'logistica':
        return redirect('ventas:pedidos_logistica')

    # Métricas generales
    total_proveedores = Proveedor.objects.count()
    total_productos = Producto.objects.count()
    total_materias_primas = MateriaPrima.objects.count()
    total_clientes = Cliente.objects.count()
    total_ventas = Venta.objects.count()
    ordenes_activas = OrdenProduccion.objects.filter(estado__in=['pendiente', 'en_progreso']).count()

    # Ventas del mes actual y anterior
    today = datetime.today()
    mes_actual = today.month
    anio_actual = today.year
    mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
    anio_anterior = anio_actual if mes_actual > 1 else anio_actual - 1
    ventas_mes_actual = Venta.objects.filter(fecha__year=anio_actual, fecha__month=mes_actual).aggregate(total=Sum('total'))['total'] or 0
    ventas_mes_anterior = Venta.objects.filter(fecha__year=anio_anterior, fecha__month=mes_anterior).aggregate(total=Sum('total'))['total'] or 0
    crecimiento_ventas = ventas_mes_actual - ventas_mes_anterior

    # Ticket promedio de venta (mes actual)
    ventas_count_mes_actual = Venta.objects.filter(fecha__year=anio_actual, fecha__month=mes_actual).count()
    ticket_promedio = ventas_mes_actual / ventas_count_mes_actual if ventas_count_mes_actual else 0

    # Top 5 productos más vendidos (mes actual)
    top_productos_qs = DetalleVenta.objects.filter(venta__fecha__year=anio_actual, venta__fecha__month=mes_actual)
    top_productos_qs = top_productos_qs.values('producto__nombre').annotate(total_cant=Sum('cantidad')).order_by('-total_cant')[:5]
    top_productos = [(p['producto__nombre'], int(p['total_cant'] or 0)) for p in top_productos_qs]

    # Productos con stock bajo (menos de 5)
    productos_stock_bajo = Producto.objects.filter(stock_actual__lte=5, activo=True).order_by('stock_actual')[:5]

    # Materias primas con stock bajo
    materias_primas_stock_bajo = MateriaPrima.objects.filter(stock_actual__lte=F('stock_minimo'), activo=True).order_by('stock_actual')[:5]

    # Clientes nuevos este mes
    clientes_nuevos = Cliente.objects.filter(fecha_registro__year=anio_actual, fecha_registro__month=mes_actual).count()

    # Órdenes de producción pendientes o en proceso
    ordenes_pendientes = OrdenProduccion.objects.filter(estado__in=['pendiente', 'en_progreso']).count()

    # Para gráficas históricas (últimos 6 meses)
    months = _last_n_months(6)
    ventas_labels = []
    ventas_values = []
    for y, m in months:
        ventas_count = Venta.objects.filter(fecha__year=y, fecha__month=m).count()
        ventas_labels.append(f"{m:02d}/{str(y)[-2:]}")
        ventas_values.append(ventas_count)

    context = {
        'total_proveedores': total_proveedores,
        'total_productos': total_productos,
        'total_materias_primas': total_materias_primas,
        'total_clientes': total_clientes,
        'total_ventas': total_ventas,
        'ordenes_activas': ordenes_activas,
        'ventas_mes_actual': ventas_mes_actual,
        'ventas_mes_anterior': ventas_mes_anterior,
        'crecimiento_ventas': crecimiento_ventas,
        'ticket_promedio': ticket_promedio,
        'top_productos': top_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'materias_primas_stock_bajo': materias_primas_stock_bajo,
        'clientes_nuevos': clientes_nuevos,
        'ordenes_pendientes': ordenes_pendientes,
        'ventas_labels': ventas_labels,
        'ventas_values': ventas_values,
    }
    return render(request, 'dashboard/index.html', context)


def admin_dashboard(request):
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    stats = {
        'total_proveedores': Proveedor.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_materias_primas': MateriaPrima.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_ventas': Venta.objects.count(),
        'ordenes_produccion_activas': OrdenProduccion.objects.filter(estado__in=['pendiente', 'en_progreso']).count(),
    }
    return render(request, 'dashboard/admin_dashboard.html', {'stats': stats})
