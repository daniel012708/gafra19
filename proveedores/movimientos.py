from django.db import models
from django.contrib.auth.models import User

class ProveedorMovimiento(models.Model):
    ACCION_CHOICES = [
        ('CREADO', 'Creado'),
        ('EDITADO', 'Editado'),
        ('ELIMINADO', 'Eliminado'),
    ]
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, related_name='movimientos')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=10, choices=ACCION_CHOICES)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Movimiento de Proveedor'
        verbose_name_plural = 'Movimientos de Proveedores'

    def __str__(self):
        return f"{self.get_accion_display()} por {self.usuario} el {self.fecha:%Y-%m-%d %H:%M}"