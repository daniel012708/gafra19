from django import forms
from .models import DetalleVenta

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'precio_unitario': forms.HiddenInput(),
            'subtotal': forms.HiddenInput(),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None:
            # No se permiten números negativos
            if cantidad < 0:
                raise forms.ValidationError('La cantidad no puede ser negativa.')
            if cantidad == 0:
                raise forms.ValidationError('La cantidad debe ser mayor a 0.')
            if cantidad > 10000:
                raise forms.ValidationError('La cantidad no puede exceder 10,000 unidades.')
        return cantidad

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        if not producto:
            self.add_error('producto', 'Debe seleccionar un producto.')

        if producto and cantidad:
            # Validar stock disponible
            if cantidad < 0:
                self.add_error('cantidad', 'La cantidad no puede ser negativa.')
            elif cantidad == 0:
                self.add_error('cantidad', 'La cantidad debe ser mayor a 0.')
            elif cantidad > producto.stock_actual:
                self.add_error('cantidad', f'No hay suficiente stock. Stock disponible: {producto.stock_actual}')

        return cleaned_data
