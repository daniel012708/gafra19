from django.db import models
from proveedores.models import Proveedor

class MateriaPrima(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    marca = models.CharField(max_length=100, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    UNIDADES = [
        ('kg', 'Kilogramo (kg)'),
        ('g', 'Gramo (g)'),
        ('l', 'Litro (l)'),
        ('ml', 'Mililitro (ml)'),
        ('m', 'Metro (m)'),
        ('cm', 'Centímetro (cm)'),
        ('pz', 'Pieza (pz)'),
        ('caja', 'Caja'),
        ('bulto', 'Bulto'),
        ('otro', 'Otro'),
    ]
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES, default='pz')
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ubicacion = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código automático tipo MP-0001
            last = MateriaPrima.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.codigo = f"MP-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.proveedor.nombre}"

    class Meta:
        verbose_name = 'Materia Prima'
        verbose_name_plural = 'Materias Primas'

class MovimientoMateriaPrima(models.Model):
    TIPO_MOVIMIENTO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    )

    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    motivo = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.materia_prima.nombre}"

    class Meta:
        verbose_name = 'Movimiento de Materia Prima'
        verbose_name_plural = 'Movimientos de Materia Prima'
        ordering = ['-fecha']
