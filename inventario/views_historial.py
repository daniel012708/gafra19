from django.views.generic import ListView
from .models import MovimientoMateriaPrima, MateriaPrima
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

class HistorialMateriaPrimaView(LoginRequiredMixin, ListView):
    model = MovimientoMateriaPrima
    template_name = 'inventario/historial_materia_prima.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_queryset(self):
        self.materia = get_object_or_404(MateriaPrima, pk=self.kwargs['pk'])
        return MovimientoMateriaPrima.objects.filter(materia_prima=self.materia).order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materia'] = self.materia
        return context
