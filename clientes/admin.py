from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'documento', 'telefono', 'email', 'fecha_registro')
    search_fields = ('nombre', 'documento', 'email')
    readonly_fields = ('fecha_registro',)
