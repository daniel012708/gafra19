from django.contrib import admin
from .models import Categoria, Producto, Receta, IngredienteReceta

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class IngredienteRecetaInline(admin.TabularInline):
    model = IngredienteReceta
    extra = 1
    autocomplete_fields = ['materia_prima']

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tiempo_produccion', 'activo')
    list_filter = ('activo',)
    search_fields = ('producto__nombre',)
    inlines = [IngredienteRecetaInline]

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_venta', 'stock_actual', 'activo')
    list_filter = ('categoria', 'activo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información del Producto', {
            'fields': ('codigo', 'nombre', 'descripcion', 'imagen', 'categoria')
        }),
        ('Precios y Stock', {
            'fields': ('precio_costo', 'precio_venta', 'stock_actual')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )
