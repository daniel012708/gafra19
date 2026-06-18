from django import forms
from django.forms import inlineformset_factory
from .models import Receta, IngredienteReceta

# Formulario para ingredientes de la receta (BOM)
class IngredienteRecetaForm(forms.ModelForm):
    class Meta:
        model = IngredienteReceta
        fields = ['materia_prima', 'cantidad_requerida']
        widgets = {
            'materia_prima': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_requerida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Cantidad por unidad'}),
        }

# Formset para BOM
IngredienteRecetaFormSet = inlineformset_factory(
    Receta, IngredienteReceta,
    form=IngredienteRecetaForm,
    extra=1,
    can_delete=True
)
from django import forms
from .models import Producto


from inventario.models import MateriaPrima

class ProductoForm(forms.ModelForm):
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if Producto.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe un producto con ese nombre.')
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        precio_venta = cleaned_data.get('precio_venta')
        errores = {}
        if precio_venta is not None and (precio_venta < 0 or precio_venta > 1000000):
            errores['precio_venta'] = 'El precio de venta debe estar entre 0 y 1,000,000.'
        if errores:
            raise forms.ValidationError(errores)
        return cleaned_data

    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'imagen', 'categoria',
            'precio_venta'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre comercial', 'maxlength': '200', 'minlength': '2', 'autocomplete': 'off'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada', 'maxlength': '500'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Precio de venta', 'min': '0', 'max': '1000000'}),
        }
