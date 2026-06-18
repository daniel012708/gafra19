from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from inventario.models import MateriaPrima

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        mensaje_recibido = request.POST.get('Body', '').strip().lower()
        respuesta = procesar_mensaje(mensaje_recibido)
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message>{respuesta}</Message></Response>"""
        return HttpResponse(xml, content_type='text/xml')
    return HttpResponse('ok')

def procesar_mensaje(texto):
    if texto == 'stock':
        materias = MateriaPrima.objects.filter(activo=True)
        alertas = [m for m in materias if m.stock_actual <= m.stock_minimo]
        if not alertas:
            return "✅ Todo el inventario está bien, ninguna materia prima está baja."
        lines = ["⚠️ Materias primas bajas:\n"]
        for m in alertas:
            lines.append(f"• {m.nombre}: {m.stock_actual} {m.unidad_medida} (mínimo: {m.stock_minimo})")
        return "\n".join(lines)

    elif texto == 'ventas hoy':
        from ventas.models import Venta
        from django.utils import timezone
        hoy = timezone.now().date()
        ventas = Venta.objects.filter(fecha__date=hoy)
        completadas = ventas.filter(estado='completada')
        total = sum(v.total for v in completadas)
        return (
            f"💰 Ventas de hoy ({hoy}):\n"
            f"• Total ventas: {ventas.count()}\n"
            f"• Completadas: {completadas.count()}\n"
            f"• Monto total: ${total:,.0f}"
        )

    elif texto == 'ordenes':
        from produccion.models import OrdenProduccion
        ordenes = OrdenProduccion.objects.filter(estado__in=['pendiente', 'en_progreso'])
        if not ordenes:
            return "No hay órdenes de producción activas."
        lines = ["📦 Órdenes activas:\n"]
        for o in ordenes:
            lines.append(f"• OP-{o.id}: {o.producto.nombre} ({o.cantidad_a_producir} uds) — {o.get_estado_display()}")
        return "\n".join(lines)

    else:
        return (
            "Hola! Estos son los comandos disponibles:\n\n"
            "• *stock* — ver materias primas bajas\n"
            "• *ventas hoy* — resumen de ventas del día\n"
            "• *ordenes* — órdenes de producción activas"
        )