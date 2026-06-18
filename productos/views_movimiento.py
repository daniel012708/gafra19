from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms_movimiento import ProductoMovimientoForm
from .models import ProductoMovimiento, Producto
from django.contrib.auth.models import User

class ProductoMovimientoCreateView(LoginRequiredMixin, FormView):
    template_name = 'productos/movimiento_form.html'
    form_class = ProductoMovimientoForm
    success_url = reverse_lazy('productos:historial_general')

    def form_valid(self, form):
        movimiento = form.save(commit=False)
        if self.request.user.is_authenticated:
            movimiento.usuario = self.request.user.username
        # Actualiza el stock del producto
        if movimiento.tipo == 'entrada':
            movimiento.producto.stock_actual += movimiento.cantidad
        elif movimiento.tipo == 'salida':
            movimiento.producto.stock_actual -= movimiento.cantidad
        movimiento.producto.save()
        movimiento.save()
        return super().form_valid(form)
