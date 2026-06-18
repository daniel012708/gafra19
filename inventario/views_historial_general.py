from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import MovimientoMateriaPrima

class HistorialGeneralMateriaPrimaView(LoginRequiredMixin, ListView):
    model = MovimientoMateriaPrima
    template_name = 'inventario/historial_general_materia_prima.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_queryset(self):
        return MovimientoMateriaPrima.objects.select_related('materia_prima').order_by('-fecha')
