from django import forms
from .models import Producto, ProductoMovimiento

class ProductoMovimientoForm(forms.ModelForm):
    class Meta:
        model = ProductoMovimiento
        fields = ['producto', 'tipo', 'cantidad', 'motivo']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Cantidad'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Observaciones'}),
        }
