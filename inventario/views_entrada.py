from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.shortcuts import get_object_or_404, redirect
from .models import MateriaPrima, MovimientoMateriaPrima
from .forms_entrada import EntradaMateriaPrimaForm

class EntradaMateriaPrimaView(LoginRequiredMixin, FormView):
    template_name = 'inventario/entrada_materia_prima.html'
    form_class = EntradaMateriaPrimaForm

    def dispatch(self, request, *args, **kwargs):
        self.materia = get_object_or_404(MateriaPrima, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materia'] = self.materia
        return context

    def form_valid(self, form):
        cantidad = form.cleaned_data['cantidad']
        precio_unitario = form.cleaned_data.get('precio_unitario')
        motivo = form.cleaned_data.get('motivo')
        self.materia.stock_actual += cantidad
        self.materia.save()
        MovimientoMateriaPrima.objects.create(
            materia_prima=self.materia,
            tipo='entrada',
            cantidad=cantidad,
            precio_unitario=precio_unitario or self.materia.precio_unitario,
            motivo=motivo or 'Entrada de mercancía',
            # usuario=self.request.user  # Si agregas campo usuario en el modelo
        )
        return redirect(reverse_lazy('inventario:list'))
