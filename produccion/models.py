from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto, Receta
from inventario.models import MateriaPrima

class OrdenProduccion(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    cantidad_a_producir = models.IntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OP-{self.id} - {self.producto.nombre} ({self.cantidad_a_producir})"

    def puede_iniciar(self):
        """Verifica si hay suficientes materias primas para iniciar la producción"""
        for ingrediente in self.receta.ingredientes.all():
            cantidad_necesaria = ingrediente.cantidad_requerida * self.cantidad_a_producir
            if ingrediente.materia_prima.stock_actual < cantidad_necesaria:
                return False
        return True

    def consumir_materias_primas(self):
        """Consume las materias primas del inventario"""
        for ingrediente in self.receta.ingredientes.all():
            cantidad_consumir = ingrediente.cantidad_requerida * self.cantidad_a_producir
            ingrediente.materia_prima.stock_actual -= cantidad_consumir
            ingrediente.materia_prima.save()

            # Registrar movimiento
            from inventario.models import MovimientoMateriaPrima
            MovimientoMateriaPrima.objects.create(
                materia_prima=ingrediente.materia_prima,
                tipo='salida',
                cantidad=cantidad_consumir,
                motivo=f'Consumo para OP-{self.id}'
            )

    def producir_productos(self):
        """Agrega los productos terminados al inventario y registra movimiento"""
        self.producto.stock_actual += self.cantidad_a_producir
        self.producto.save()
        # Registrar movimiento en historial de productos
        from productos.models import ProductoMovimiento
        ProductoMovimiento.objects.create(
            producto=self.producto,
            tipo='entrada',
            cantidad=self.cantidad_a_producir,
            usuario=str(self.responsable) if self.responsable else '',
            motivo=f'Ingreso por OP-{self.id}'
        )

    class Meta:
        verbose_name = 'Orden de Producción'
        verbose_name_plural = 'Órdenes de Producción'
        ordering = ['-fecha_creacion']

class ProduccionDiaria(models.Model):
    orden_produccion = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE)
    fecha = models.DateField()
    cantidad_producida = models.IntegerField(default=0)
    tiempo_trabajado = models.IntegerField(help_text='Tiempo en minutos', default=0)
    observaciones = models.TextField(blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.orden_produccion} - {self.fecha}"

    class Meta:
        verbose_name = 'Producción Diaria'
        verbose_name_plural = 'Producciones Diarias'
        unique_together = ['orden_produccion', 'fecha']
