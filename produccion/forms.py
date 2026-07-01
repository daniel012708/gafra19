from django import forms
from django.core.validators import RegexValidator
import re
from productos.models import Producto

from .models import OrdenProduccion, ProduccionDiaria


class OrdenProduccionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar productos activos que tienen receta activa
        self.fields['producto'].queryset = Producto.objects.filter(receta__activo=True, activo=True)

    class Meta:
        model = OrdenProduccion
        fields = ['producto', 'cantidad_a_producir', 'notas']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_a_producir': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '500'}),
        }

    def clean_notas(self):
        notas = self.cleaned_data.get('notas', '')
        if notas:
            notas = notas.strip()
            if not notas:
                raise forms.ValidationError('Las notas no pueden contener solo espacios.')
        return notas

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad_a_producir')
        notas = cleaned_data.get('notas')

        errores = {}

        # Limpiar espacios en notas
        if notas:
            cleaned_data['notas'] = notas.strip()

        # Validar que el producto sea obligatorio
        if not producto:
            errores['producto'] = 'Debe seleccionar un producto.'

        # Validar cantidad - no números negativos
        if cantidad is not None:
            if cantidad < 0:
                errores['cantidad_a_producir'] = 'La cantidad no puede ser negativa.'
            elif cantidad == 0:
                errores['cantidad_a_producir'] = 'La cantidad debe ser mayor a 0.'
            elif cantidad > 1000000:
                errores['cantidad_a_producir'] = 'La cantidad no puede exceder 1,000,000.'

        if errores:
            raise forms.ValidationError(errores)

        # Validar solo si el producto y cantidad son válidos
        if producto and cantidad and cantidad > 0:
            # Verificar que el producto tenga receta
            if not hasattr(producto, 'receta') or not producto.receta.activo:
                raise forms.ValidationError('Este producto no tiene una receta activa definida.')

            # Verificar disponibilidad de materias primas
            for ingrediente in producto.receta.ingredientes.all():
                cantidad_necesaria = ingrediente.cantidad_requerida * cantidad
                if ingrediente.materia_prima.stock_actual < cantidad_necesaria:
                    raise forms.ValidationError(
                        f'No hay suficiente {ingrediente.materia_prima.nombre}. '
                        f'Necesario: {cantidad_necesaria}, Disponible: {ingrediente.materia_prima.stock_actual}'
                    )

        return cleaned_data


class ProduccionDiariaForm(forms.ModelForm):
    class Meta:
        model = ProduccionDiaria
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '500'}),
        }

    def clean_observaciones(self):
        observaciones = self.cleaned_data.get('observaciones', '')
        if observaciones:
            observaciones = observaciones.strip()
            if not observaciones:
                raise forms.ValidationError('Las observaciones no pueden contener solo espacios.')
        return observaciones
