from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import ProductoMovimiento

class HistorialGeneralProductoView(LoginRequiredMixin, ListView):
    model = ProductoMovimiento
    template_name = 'productos/historial_general_producto.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_queryset(self):
        return ProductoMovimiento.objects.select_related('producto').order_by('-fecha')
