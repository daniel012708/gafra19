from django import forms
from django.contrib.auth.models import User
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    username = forms.CharField(
        min_length=4,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 4 caracteres.'
    )
    first_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 2 caracteres.'
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 2 caracteres.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Debe ser un email válido.'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        min_length=8,
        help_text='Mínimo 8 caracteres, debe incluir letras, números y símbolos.'
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

        # Validar contraseñas
        if password or password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', 'Las contraseñas no coinciden.')
            # Validar seguridad de la contraseña
            import re
            if password:
                if len(password) < 8:
                    self.add_error('password', 'La contraseña debe tener al menos 8 caracteres.')
                if not re.search(r'[A-Z]', password):
                    self.add_error('password', 'Debe incluir al menos una letra mayúscula.')
                if not re.search(r'[a-z]', password):
                    self.add_error('password', 'Debe incluir al menos una letra minúscula.')
                if not re.search(r'\d', password):
                    self.add_error('password', 'Debe incluir al menos un número.')
                if not re.search(r'[^A-Za-z0-9]', password):
                    self.add_error('password', 'Debe incluir al menos un símbolo.')

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
