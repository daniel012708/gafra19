from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    # 'cliente_nombre' was removed when Venta switched to a FK to clientes.Cliente.
    # Use 'cliente' here so the admin displays the Cliente __str__ (nombre),
    # or define a helper method if you need a customized display.
    list_display = ('numero_venta', 'cliente', 'vendedor', 'estado', 'total', 'fecha')
    list_filter = ('estado', 'fecha', 'vendedor')
    search_fields = ('numero_venta',)
    readonly_fields = ('fecha',)
    inlines = [DetalleVentaInline]
    fieldsets = (
        ('Información de Venta', {
            'fields': ('numero_venta', 'fecha', 'vendedor', 'estado')
        }),
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Totales', {
            'fields': ('descuento', 'impuesto', 'total')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha',)
    search_fields = ('venta__numero_venta', 'producto__nombre')
