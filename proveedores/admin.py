from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'email', 'ciudad', 'activo')
    list_filter = ('activo', 'ciudad', 'pais', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'telefono')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'contacto', 'telefono', 'email')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'pais')
        }),
        ('Otros', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
