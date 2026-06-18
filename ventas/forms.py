
from django import forms
from .models import Venta, DetalleVenta
from django.forms import inlineformset_factory
from .forms_detalle import DetalleVentaForm

# Formset para los detalles de la venta

DetalleFormset = inlineformset_factory(
    parent_model=Venta,
    model=DetalleVenta,
    form=DetalleVentaForm,
    fields=['producto', 'cantidad', 'precio_unitario', 'subtotal'],
    extra=1,
    can_delete=True,
)


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'estado', 'observaciones']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 500, 'placeholder': 'Observaciones (máx. 500 caracteres)'}),
        }

    def clean_observaciones(self):
        obs = self.cleaned_data.get('observaciones', '').strip()
        if len(obs) > 500:
            raise forms.ValidationError('Las observaciones no pueden superar los 500 caracteres.')
        return obs
