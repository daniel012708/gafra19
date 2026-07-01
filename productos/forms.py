from django import forms
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator
import re
from .models import Receta, IngredienteReceta

# Formulario para ingredientes de la receta (BOM)
class IngredienteRecetaForm(forms.ModelForm):
    class Meta:
        model = IngredienteReceta
        fields = ['materia_prima', 'cantidad_requerida']
        widgets = {
            'materia_prima': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_requerida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Cantidad por unidad', 'min': '0.01'}),
        }

    def clean_cantidad_requerida(self):
        cantidad = self.cleaned_data.get('cantidad_requerida')
        if cantidad is not None:
            if cantidad < 0.01:
                raise forms.ValidationError('La cantidad debe ser mayor a 0.')
            if cantidad > 10000:
                raise forms.ValidationError('La cantidad no puede exceder 10,000.')
        return cantidad

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
        nombre = self.cleaned_data.get('nombre', '')
        if nombre:
            nombre = nombre.strip()
            if not nombre:
                raise forms.ValidationError('El nombre no puede contener solo espacios.')
            
            # Validar que no contenga solo números
            if nombre.isdigit():
                raise forms.ValidationError('El nombre no puede contener solo números.')
            
            qs = Producto.objects.filter(nombre__iexact=nombre)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un producto con ese nombre.')
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '')
        if descripcion:
            descripcion = descripcion.strip()
            if not descripcion:
                raise forms.ValidationError('La descripción no puede contener solo espacios.')
        return descripcion

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        descripcion = cleaned_data.get('descripcion')
        precio_venta = cleaned_data.get('precio_venta')
        categoria = cleaned_data.get('categoria')

        errores = {}

        # Limpiar espacios
        if nombre:
            cleaned_data['nombre'] = nombre.strip()
        if descripcion:
            cleaned_data['descripcion'] = descripcion.strip()

        # Validar que nombre sea obligatorio
        if not nombre or not nombre.strip():
            errores['nombre'] = 'El nombre es obligatorio.'

        # Validar precio de venta - no números negativos
        if precio_venta is not None:
            if precio_venta < 0:
                errores['precio_venta'] = 'El precio de venta no puede ser negativo.'
            elif precio_venta == 0:
                errores['precio_venta'] = 'El precio de venta debe ser mayor a 0.'
            elif precio_venta > 1000000:
                errores['precio_venta'] = 'El precio de venta no puede exceder 1,000,000.'

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
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Precio de venta', 'min': '0.01', 'max': '1000000'}),
        }
