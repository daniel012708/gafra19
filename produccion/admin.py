from django.contrib import admin
from .models import OrdenProduccion, ProduccionDiaria


@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'cantidad_a_producir', 'estado', 'fecha_creacion', 'responsable')
    list_filter = ('estado', 'fecha_creacion', 'responsable')
    search_fields = ('producto__nombre', 'id')
    readonly_fields = ('fecha_creacion',)

@admin.register(ProduccionDiaria)
class ProduccionDiariaAdmin(admin.ModelAdmin):
    list_display = ('orden_produccion', 'fecha', 'cantidad_producida', 'tiempo_trabajado', 'responsable')
    list_filter = ('fecha', 'responsable')
    search_fields = ('orden_produccion__producto__nombre',)
