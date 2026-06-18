from django import forms
from .models import MateriaPrima


class MateriaPrimaForm(forms.ModelForm):
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if MateriaPrima.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe una materia prima con ese nombre.')
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        stock_actual = cleaned_data.get('stock_actual')
        stock_minimo = cleaned_data.get('stock_minimo')
        precio_unitario = cleaned_data.get('precio_unitario')
        errores = {}
        if stock_actual is not None and (stock_actual < 0 or stock_actual > 1000000):
            errores['stock_actual'] = 'El stock actual debe estar entre 0 y 1,000,000.'
        if stock_minimo is not None and (stock_minimo < 0 or stock_minimo > 1000000):
            errores['stock_minimo'] = 'El stock mínimo debe estar entre 0 y 1,000,000.'
        if precio_unitario is not None and (precio_unitario < 0 or precio_unitario > 1000000):
            errores['precio_unitario'] = 'El precio unitario debe estar entre 0 y 1,000,000.'
        if errores:
            raise forms.ValidationError(errores)
        return cleaned_data

    class Meta:
        model = MateriaPrima
        fields = [
            'nombre', 'descripcion', 'marca', 'proveedor', 'precio_unitario',
            'unidad_medida', 'stock_actual', 'stock_minimo', 'ubicacion', 'observaciones', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200', 'minlength': '2', 'autocomplete': 'off'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '500'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1000000'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-select'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1000000'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '1000000'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'maxlength': '300'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
