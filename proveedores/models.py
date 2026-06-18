
from django.db import models
from .movimientos import ProveedorMovimiento

class Proveedor(models.Model):
    nombre = models.CharField("Nombre comercial", max_length=150)
    razon_social = models.CharField("Razón social", max_length=200, blank=True)
    rfc = models.CharField("RFC", max_length=13, blank=True)
    contacto = models.CharField("Nombre de contacto", max_length=100)
    telefono = models.CharField("Teléfono", max_length=20)
    email = models.EmailField("Correo electrónico")
    direccion = models.CharField("Dirección", max_length=255)
    ciudad = models.CharField("Ciudad", max_length=100)
    estado = models.CharField("Estado", max_length=100, blank=True)
    pais = models.CharField("País", max_length=100)
    codigo_postal = models.CharField("Código postal", max_length=10, blank=True)
    tipo = models.CharField("Tipo de proveedor", max_length=50, choices=[('Nacional', 'Nacional'), ('Extranjero', 'Extranjero')], default='Nacional')
    sitio_web = models.URLField("Sitio web", max_length=200, blank=True)
    activo = models.BooleanField("Activo", default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
