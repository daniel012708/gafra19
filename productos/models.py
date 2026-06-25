from django.db import models
from proveedores.models import Proveedor
from gafra.soft_delete import SoftDeleteModel

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

class Producto(SoftDeleteModel):
    codigo = models.CharField(max_length=50, unique=True, editable=False)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        estado = " [ELIMINADO]" if self.deleted else ""
        return f"{self.codigo} - {self.nombre}{estado}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código automático tipo PRD-0001
            last = Producto.objects.all_including_deleted().order_by('-id').first()
            if last and last.codigo and last.codigo.startswith('PRD-'):
                try:
                    last_num = int(last.codigo.split('-')[1])
                except Exception:
                    last_num = last.id
            else:
                last_num = 0
            self.codigo = f"PRD-{last_num+1:04d}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

class Receta(SoftDeleteModel):
    producto = models.OneToOneField(Producto, on_delete=models.PROTECT, related_name='receta')
    descripcion = models.TextField(blank=True)
    tiempo_produccion = models.IntegerField(help_text='Tiempo en minutos', default=60)
    activo = models.BooleanField(default=True)

    def __str__(self):
        estado = " [ELIMINADA]" if self.deleted else ""
        return f"Receta de {self.producto.nombre}{estado}"

    class Meta:
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'


# Historial de movimientos de productos
class ProductoMovimiento(SoftDeleteModel):
    TIPO_MOVIMIENTO = [
        ('creacion', 'Creación'),
        ('modificacion', 'Modificación'),
        ('entrada', 'Entrada stock'),
        ('salida', 'Salida stock'),
        ('ajuste', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usuario = models.CharField(max_length=150, blank=True)
    motivo = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre}"

    class Meta:
        verbose_name = 'Movimiento de Producto'
        verbose_name_plural = 'Movimientos de Producto'
        ordering = ['-fecha']

class IngredienteReceta(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='ingredientes')
    materia_prima = models.ForeignKey('inventario.MateriaPrima', on_delete=models.CASCADE)
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.materia_prima.nombre} - {self.cantidad_requerida} {self.materia_prima.unidad_medida}"

    class Meta:
        verbose_name = 'Ingrediente de Receta'
        verbose_name_plural = 'Ingredientes de Receta'
