from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    username = forms.CharField(
        min_length=4,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 4 caracteres. Solo letras, números, puntos, guiones e guiones bajos.',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._-]+$',
                message='El nombre de usuario solo puede contener letras, números, puntos, guiones e guiones bajos.',
                code='invalid_username'
            )
        ]
    )
    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 2 caracteres. Solo letras, espacios y apóstrofos.',
        validators=[
            RegexValidator(
                regex=r"^[a-záéíóúàèìòùâêîôûäëïöüñ\s\'-]+$",
                message='El nombre solo puede contener letras, espacios, apóstrofos y guiones.',
                code='invalid_first_name',
                flags=re.IGNORECASE
            )
        ]
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 2 caracteres. Solo letras, espacios y apóstrofos.',
        validators=[
            RegexValidator(
                regex=r"^[a-záéíóúàèìòùâêîôûäëïöüñ\s\'-]+$",
                message='El apellido solo puede contener letras, espacios, apóstrofos y guiones.',
                code='invalid_last_name',
                flags=re.IGNORECASE
            )
        ]
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Debe ser un email válido.'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        min_length=8,
        help_text='Mínimo 8 caracteres. Debe incluir mayúsculas, minúsculas, números y símbolos.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        min_length=8,
        help_text='Repite la contraseña.'
    )

    class Meta:
        model = Usuario
        fields = ['rol', 'telefono', 'activo']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Si estamos editando, cargar datos del User relacionado
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            # No mostrar contraseña en edición
            self.fields['password'].widget = forms.HiddenInput()
            self.fields['password_confirm'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        telefono = cleaned_data.get('telefono')
        rol = cleaned_data.get('rol')

        # Validar que se seleccione un rol
        if not rol:
            self.add_error('rol', 'Debe seleccionar un rol.')

        # Limpiar espacios en blanco al inicio y final
        if username:
            cleaned_data['username'] = username.strip()
        if first_name:
            cleaned_data['first_name'] = first_name.strip()
        if last_name:
            cleaned_data['last_name'] = last_name.strip()
        if email:
            cleaned_data['email'] = email.strip()
        if telefono:
            cleaned_data['telefono'] = telefono.strip()

        # Validar que nombre no contenga números
        if first_name and re.search(r'\d', first_name):
            self.add_error('first_name', 'El nombre no puede contener números.')

        # Validar que apellido no contenga números
        if last_name and re.search(r'\d', last_name):
            self.add_error('last_name', 'El apellido no puede contener números.')

        # Validar que nombre no esté vacío después de espacios
        if first_name and not first_name.strip():
            self.add_error('first_name', 'El nombre no puede contener solo espacios.')

        # Validar que apellido no esté vacío después de espacios
        if last_name and not last_name.strip():
            self.add_error('last_name', 'El apellido no puede contener solo espacios.')

        # Validar teléfono
        if telefono:
            # No permitir números negativos o caracteres inválidos al inicio
            if telefono[0] == '-':
                self.add_error('telefono', 'El teléfono no puede comenzar con un guión (números negativos no permitidos).')
            # Solo dígitos, espacios, guiones, paréntesis y símbolo +
            if not re.match(r'^[+]?[(]?[\d\s\-.)]+$', telefono):
                self.add_error('telefono', 'Formato de teléfono inválido. Solo se permiten dígitos, espacios, guiones, paréntesis y símbolo +.')
            # No permitir guiones seguidos
            elif '--' in telefono:
                self.add_error('telefono', 'No se permiten guiones consecutivos.')
            elif len(re.sub(r'\D', '', telefono)) < 7:
                self.add_error('telefono', 'El teléfono debe tener al menos 7 dígitos.')
            elif len(re.sub(r'\D', '', telefono)) > 15:
                self.add_error('telefono', 'El teléfono no puede tener más de 15 dígitos.')

        # Validar unicidad de username
        if username:
            qs = User.objects.filter(username=username)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.user.pk)
            if qs.exists():
                self.add_error('username', 'Ya existe un usuario con ese nombre de usuario.')

        # Validar unicidad de email
        if email:
            qs = User.objects.filter(email=email)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.user.pk)
            if qs.exists():
                self.add_error('email', 'Ya existe un usuario con ese email.')

        # Validar contraseñas - obligatorias al crear nuevo usuario
        if not self.instance or not self.instance.pk:
            # Creando nuevo usuario
            if not password:
                self.add_error('password', 'La contraseña es obligatoria.')
            if not password_confirm:
                self.add_error('password_confirm', 'Debe confirmar la contraseña.')

        # Validar que las contraseñas coincidan
        if (password or password_confirm) and password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')

        # Validar seguridad de la contraseña
        if password:
            errors = []
            if len(password) < 8:
                errors.append('La contraseña debe tener al menos 8 caracteres.')
            if not re.search(r'[A-Z]', password):
                errors.append('Debe incluir al menos una letra mayúscula.')
            if not re.search(r'[a-z]', password):
                errors.append('Debe incluir al menos una letra minúscula.')
            if not re.search(r'\d', password):
                errors.append('Debe incluir al menos un número.')
            if not re.search(r'[^A-Za-z0-9]', password):
                errors.append('Debe incluir al menos un símbolo especial.')
            
            if errors:
                self.add_error('password', ' '.join(errors))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Crear o actualizar el User relacionado
        if self.instance and self.instance.pk:
            # Editando usuario existente
            user = self.instance.user
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.is_active = bool(self.cleaned_data.get('activo', True))
            user.save()
        else:
            # Creando nuevo usuario
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            user.is_active = bool(self.cleaned_data.get('activo', True))
            user.save(update_fields=['is_active'])
            instance.user = user

        if commit:
            instance.save()

        return instance
