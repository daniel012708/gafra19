from django import forms
from django.contrib.auth.models import User
from usuario.models import Usuario
import re

class RegistroClienteForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        }),
        help_text='Solo letras, números, guiones y guiones bajos.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        help_text='Mínimo 8 caracteres, mayúsculas, minúsculas y números.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono'
        })
    )

    class Meta:
        model = Usuario
        fields = ['telefono']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('El nombre de usuario es requerido.')
        if len(username) < 3:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError('El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('El nombre de usuario ya está registrado.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('El email es requerido.')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('La contraseña es requerida.')
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una mayúscula.')
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('La contraseña debe contener al menos una minúscula.')
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('La contraseña debe contener al menos un número.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        user.is_active = True
        user.save(update_fields=['is_active'])
        usuario = Usuario(user=user, rol='cliente', telefono=self.cleaned_data['telefono'], activo=True)
        if commit:
            usuario.save()
        return usuario
