from django.views.generic import ListView
from .models import ProductoMovimiento, Producto
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

class HistorialProductoView(LoginRequiredMixin, ListView):
    model = ProductoMovimiento
    template_name = 'productos/historial_producto.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_queryset(self):
        self.producto = get_object_or_404(Producto, pk=self.kwargs['pk'])
        return ProductoMovimiento.objects.filter(producto=self.producto).order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = self.producto
        return context
