from django import forms
from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    nombre = forms.CharField(
        min_length=3,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 3 caracteres.'
    )
    razon_social = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    rfc = forms.CharField(
        max_length=13,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '13'}),
        help_text='Máximo 13 caracteres.'
    )
    contacto = forms.CharField(
        min_length=3,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 3 caracteres.'
    )
    telefono = forms.CharField(
        min_length=7,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 7 dígitos.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Debe ser un email válido.'
    )
    direccion = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ciudad = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pais = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    codigo_postal = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tipo = forms.ChoiceField(
        choices=[('Nacional', 'Nacional'), ('Extranjero', 'Extranjero')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sitio_web = forms.URLField(
        max_length=200,
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    activo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'razon_social', 'rfc', 'contacto', 'telefono', 'email',
            'direccion', 'ciudad', 'estado', 'pais', 'codigo_postal', 'tipo', 'sitio_web', 'activo'
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if Proveedor.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('Ya existe un proveedor con ese email.')
        return email

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Proveedor.objects.filter(nombre=nombre).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('Ya existe un proveedor con ese nombre.')
        return nombre
