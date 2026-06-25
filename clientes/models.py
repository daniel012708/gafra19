from django.db import models
from gafra.soft_delete import SoftDeleteModel


class Cliente(SoftDeleteModel):
    nombre = models.CharField(max_length=150)
    documento = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        estado = " (ELIMINADO)" if self.deleted else ""
        return f"{self.nombre}{estado}"

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'