from django import forms
from django.core.validators import RegexValidator
import re
from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    nombre = forms.CharField(
        min_length=3,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 3 caracteres. Solo letras, números y espacios.',
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9\s\&\.\-'ñáéíóúàèìòùâêîôûäëïöü]+$",
                message='El nombre solo puede contener letras, números, espacios y algunos caracteres especiales.',
                code='invalid_nombre',
                flags=re.IGNORECASE
            )
        ]
    )
    razon_social = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Solo letras, números y espacios.',
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9\s\&\.\-'ñáéíóúàèìòùâêîôûäëïöü]+$",
                message='La razón social solo puede contener letras, números, espacios y algunos caracteres especiales.',
                code='invalid_razon_social',
                flags=re.IGNORECASE
            )
        ]
    )
    rfc = forms.CharField(
        max_length=13,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '13'}),
        help_text='Máximo 13 caracteres. Solo caracteres alfanuméricos.',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message='El RFC solo puede contener letras y números.',
                code='invalid_rfc'
            )
        ]
    )
    contacto = forms.CharField(
        min_length=3,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 3 caracteres. Solo letras y espacios.',
        validators=[
            RegexValidator(
                regex=r"^[a-záéíóúàèìòùâêîôûäëïöüñ\s\'-]+$",
                message='El contacto solo puede contener letras, espacios, apóstrofos y guiones.',
                code='invalid_contacto',
                flags=re.IGNORECASE
            )
        ]
    )
    telefono = forms.CharField(
        min_length=7,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 7 dígitos. Formato: +34 123 456789 o (123) 456-7890'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Debe ser un email válido.'
    )
    direccion = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Solo letras, números y caracteres especiales permitidos.'
    )
    ciudad = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Solo letras y espacios.',
        validators=[
            RegexValidator(
                regex=r"^[a-záéíóúàèìòùâêîôûäëïöüñ\s\'-]+$",
                message='La ciudad solo puede contener letras, espacios, apóstrofos y guiones.',
                code='invalid_ciudad',
                flags=re.IGNORECASE
            )
        ]
    )
    estado = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Solo letras y espacios.',
        validators=[
            RegexValidator(
                regex=r"^[a-záéíóúàèìòùâêîôûäëïöüñ\s\'-]*$",
                message='El estado solo puede contener letras, espacios, apóstrofos y guiones.',
                code='invalid_estado',
                flags=re.IGNORECASE
            )
        ]
    )
    pais = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Solo letras y espacios.',
        validators=[
            RegexValidator(
                regex=r"^[a-záéíóúàèìòùâêîôûäëïöüñ\s\'-]+$",
                message='El país solo puede contener letras, espacios, apóstrofos y guiones.',
                code='invalid_pais',
                flags=re.IGNORECASE
            )
        ]
    )
    codigo_postal = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Máximo 10 caracteres. Solo letras, números y guiones.',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\-]*$',
                message='El código postal solo puede contener letras, números y guiones.',
                code='invalid_codigo_postal'
            )
        ]
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

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        razon_social = cleaned_data.get('razon_social')
        rfc = cleaned_data.get('rfc')
        contacto = cleaned_data.get('contacto')
        telefono = cleaned_data.get('telefono')
        email = cleaned_data.get('email')
        direccion = cleaned_data.get('direccion')
        ciudad = cleaned_data.get('ciudad')
        estado = cleaned_data.get('estado')
        pais = cleaned_data.get('pais')
        codigo_postal = cleaned_data.get('codigo_postal')

        # Limpiar espacios en blanco al inicio y final
        for field in ['nombre', 'razon_social', 'rfc', 'contacto', 'email', 'direccion', 'ciudad', 'estado', 'pais', 'codigo_postal', 'telefono']:
            if field in cleaned_data and cleaned_data[field]:
                cleaned_data[field] = cleaned_data[field].strip()

        # Validar nombre no esté vacío después de espacios
        if nombre and not nombre.strip():
            self.add_error('nombre', 'El nombre no puede contener solo espacios.')

        # Validar ciudad no esté vacía después de espacios
        if ciudad and not ciudad.strip():
            self.add_error('ciudad', 'La ciudad no puede contener solo espacios.')

        # Validar país no esté vacío después de espacios
        if pais and not pais.strip():
            self.add_error('pais', 'El país no puede contener solo espacios.')

        # Validar teléfono
        if telefono:
            # No permitir números negativos
            if telefono[0] == '-':
                self.add_error('telefono', 'El teléfono no puede comenzar con un guión (números negativos no permitidos).')
            # Solo dígitos, espacios, guiones, paréntesis y símbolo +
            elif not re.match(r'^[+]?[(]?[\d\s\-.)]+$', telefono):
                self.add_error('telefono', 'Formato de teléfono inválido. Solo se permiten dígitos, espacios, guiones, paréntesis y símbolo +.')
            # No permitir guiones seguidos
            elif '--' in telefono:
                self.add_error('telefono', 'No se permiten guiones consecutivos.')
            # Validar que tenga suficientes dígitos
            elif len(re.sub(r'\D', '', telefono)) < 7:
                self.add_error('telefono', 'El teléfono debe tener al menos 7 dígitos.')
            elif len(re.sub(r'\D', '', telefono)) > 15:
                self.add_error('telefono', 'El teléfono no puede tener más de 15 dígitos.')

        # Validar dirección no contenga solo números negativos
        if direccion and direccion.startswith('-'):
            self.add_error('direccion', 'La dirección no puede comenzar con un guión.')

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            email = email.strip()
            cleaned_data = self.cleaned_data
            cleaned_data['email'] = email
            if Proveedor.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('Ya existe un proveedor con ese email.')
        return email

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if nombre:
            nombre = nombre.strip()
            if Proveedor.objects.filter(nombre=nombre).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError('Ya existe un proveedor con ese nombre.')
        return nombre
