from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto
from clientes.models import Cliente
from django.db import transaction
from django.utils import timezone


class Venta(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )
    
    numero_venta = models.CharField(max_length=50, unique=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_completado = models.DateTimeField(null=True, blank=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Venta {self.numero_venta}"
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def save(self, *args, **kwargs):
        # auto generate numero_venta if not provided: consecutive per day VYYYYMMDD-0001
        if not self.numero_venta:
            today = timezone.now().date()
            prefix = today.strftime('V%Y%m%d')
            # find last with this prefix
            last = Venta.objects.filter(numero_venta__startswith=prefix).order_by('-numero_venta').first()
            if last and last.numero_venta:
                try:
                    seq = int(last.numero_venta.split('-')[-1])
                except Exception:
                    seq = 0
            else:
                seq = 0
            seq += 1
            self.numero_venta = f"{prefix}-{seq:04d}"
        super().save(*args, **kwargs)

    def recompute_total(self):
        from decimal import Decimal
        total = Decimal('0')
        for d in self.detalles.all():
            total += (d.subtotal or (d.cantidad * d.precio_unitario))
        # simple discount logic: discount = 0 if total < 100 else 0.05*total (example)
        descuento = Decimal('0')
        if total >= Decimal('100000'):  # arbitrary business rule
            descuento = total * Decimal('0.05')
        self.descuento = descuento
        self.total = total - descuento + (self.impuesto or Decimal('0'))
        self.save()

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.venta.numero_venta} - {self.producto.nombre}"
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'


class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def total(self):
        from decimal import Decimal
        total = Decimal('0')
        for item in self.items.all():
            total += item.subtotal()
        return total
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
    
    def subtotal(self):
        return self.cantidad * self.producto.precio_venta
    
    class Meta:
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        unique_together = ('carrito', 'producto')


class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.producto.nombre}"
    
    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = ('usuario', 'producto')

