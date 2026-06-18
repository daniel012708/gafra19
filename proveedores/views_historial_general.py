from django.views.generic import ListView
from .movimientos import ProveedorMovimiento
from django.contrib.auth.mixins import LoginRequiredMixin

class ProveedorHistorialGeneralView(LoginRequiredMixin, ListView):
    model = ProveedorMovimiento
    template_name = 'proveedores/proveedor_historial_general.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_queryset(self):
        return ProveedorMovimiento.objects.select_related('proveedor', 'usuario').all()
