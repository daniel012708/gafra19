from django.contrib import admin
from .models import MateriaPrima, MovimientoMateriaPrima

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proveedor', 'stock_actual', 'unidad_medida', 'precio_unitario', 'activo')
    list_filter = ('proveedor', 'activo', 'unidad_medida')
    search_fields = ('nombre', 'proveedor__nombre')
    readonly_fields = ('fecha_creacion',)

@admin.register(MovimientoMateriaPrima)
class MovimientoMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('materia_prima', 'tipo', 'cantidad', 'precio_unitario', 'motivo', 'fecha')
    list_filter = ('tipo', 'fecha', 'materia_prima__proveedor')
    search_fields = ('materia_prima__nombre', 'motivo')
    readonly_fields = ('fecha',)
    ordering = ['-fecha']
