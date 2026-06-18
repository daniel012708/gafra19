from django import forms

class EntradaMateriaPrimaForm(forms.Form):
    cantidad = forms.DecimalField(label="Cantidad recibida", min_value=0.01, decimal_places=2, max_digits=10, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    precio_unitario = forms.DecimalField(label="Precio unitario", min_value=0, decimal_places=2, max_digits=10, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    motivo = forms.CharField(label="Motivo/Observaciones", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
