from django import forms
from django.core.validators import RegexValidator
import re
from .models import MateriaPrima


class MateriaPrimaForm(forms.ModelForm):
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if nombre:
            nombre = nombre.strip()
            if not nombre:
                raise forms.ValidationError('El nombre no puede contener solo espacios.')
            
            # Validar que no contenga solo números
            if nombre.isdigit():
                raise forms.ValidationError('El nombre no puede contener solo números.')
            
            qs = MateriaPrima.objects.filter(nombre__iexact=nombre)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe una materia prima con ese nombre.')
        return nombre

    def clean_marca(self):
        marca = self.cleaned_data.get('marca', '')
        if marca:
            marca = marca.strip()
            if not marca:
                raise forms.ValidationError('La marca no puede contener solo espacios.')
        return marca

    def clean_ubicacion(self):
        ubicacion = self.cleaned_data.get('ubicacion', '')
        if ubicacion:
            ubicacion = ubicacion.strip()
            if not ubicacion:
                raise forms.ValidationError('La ubicación no puede contener solo espacios.')
        return ubicacion

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        marca = cleaned_data.get('marca')
        ubicacion = cleaned_data.get('ubicacion')
        stock_actual = cleaned_data.get('stock_actual')
        stock_minimo = cleaned_data.get('stock_minimo')
        precio_unitario = cleaned_data.get('precio_unitario')
        proveedor = cleaned_data.get('proveedor')
        unidad_medida = cleaned_data.get('unidad_medida')
        descripcion = cleaned_data.get('descripcion')
        observaciones = cleaned_data.get('observaciones')

        errores = {}

        # Limpiar espacios
        if nombre:
            cleaned_data['nombre'] = nombre.strip()
        if marca:
            cleaned_data['marca'] = marca.strip()
        if ubicacion:
            cleaned_data['ubicacion'] = ubicacion.strip()
        if descripcion:
            cleaned_data['descripcion'] = descripcion.strip()
        if observaciones:
            cleaned_data['observaciones'] = observaciones.strip()

        # Validar que nombre no sea vacío
        if not nombre or not nombre.strip():
            errores['nombre'] = 'El nombre es obligatorio.'

        # Validar stock actual - no números negativos
        if stock_actual is not None:
            if stock_actual < 0:
                errores['stock_actual'] = 'El stock actual no puede ser negativo.'
            elif stock_actual > 1000000:
                errores['stock_actual'] = 'El stock actual no puede exceder 1,000,000.'

        # Validar stock mínimo - no números negativos
        if stock_minimo is not None:
            if stock_minimo < 0:
                errores['stock_minimo'] = 'El stock mínimo no puede ser negativo.'
            elif stock_minimo > 1000000:
                errores['stock_minimo'] = 'El stock mínimo no puede exceder 1,000,000.'

        # Validar que stock actual no sea menor que stock mínimo
        if stock_actual is not None and stock_minimo is not None:
            if stock_actual < stock_minimo:
                errores['stock_actual'] = 'El stock actual no puede ser menor que el stock mínimo.'

        # Validar precio unitario - no números negativos
        if precio_unitario is not None:
            if precio_unitario < 0:
                errores['precio_unitario'] = 'El precio unitario no puede ser negativo.'
            elif precio_unitario > 1000000:
                errores['precio_unitario'] = 'El precio unitario no puede exceder 1,000,000.'
            elif precio_unitario == 0:
                errores['precio_unitario'] = 'El precio unitario debe ser mayor a 0.'

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
