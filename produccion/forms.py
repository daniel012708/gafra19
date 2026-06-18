from django import forms
from productos.models import Producto

from .models import OrdenProduccion, ProduccionDiaria


class OrdenProduccionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar productos que tienen receta
        self.fields['producto'].queryset = Producto.objects.filter(receta__activo=True)

    class Meta:
        model = OrdenProduccion
        fields = ['producto', 'cantidad_a_producir', 'notas']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_a_producir': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad_a_producir')

        if producto and cantidad:
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
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
