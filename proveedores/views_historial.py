from django.views.generic import ListView
from .movimientos import ProveedorMovimiento
from .models import Proveedor
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

class ProveedorHistorialView(LoginRequiredMixin, ListView):
    model = ProveedorMovimiento
    template_name = 'proveedores/proveedor_historial.html'
    context_object_name = 'movimientos'
    paginate_by = 20

    def get_queryset(self):
        self.proveedor = get_object_or_404(Proveedor, pk=self.kwargs['pk'])
        return ProveedorMovimiento.objects.filter(proveedor=self.proveedor)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proveedor'] = self.proveedor
        return context
