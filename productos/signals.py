from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Producto
from gafra.whatsapp import enviar_whatsapp

@receiver(post_save, sender=Producto)
def producto_guardado(sender, instance, created, **kwargs):
    if created:
        mensaje = (
            f"✅ Producto AGREGADO\n"
            f"• Nombre: {instance.nombre}\n"
            f"• Código: {instance.codigo}\n"
            f"• Precio: ${instance.precio_venta:,.0f}\n"
            f"• Stock inicial: {instance.stock_actual}"
        )
        enviar_whatsapp(mensaje)

@receiver(post_delete, sender=Producto)
def producto_eliminado(sender, instance, **kwargs):
    mensaje = (
        f"🗑️ Producto ELIMINADO\n"
        f"• Nombre: {instance.nombre}\n"
        f"• Código: {instance.codigo}"
    )
    enviar_whatsapp(mensaje)