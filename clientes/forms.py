from django import forms
from django.core.validators import RegexValidator
import re
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'minlength': 3, 'maxlength': 150, 'placeholder': 'Nombre completo'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50, 'placeholder': 'Cédula o documento'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 255, 'placeholder': 'Dirección completa'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 20, 'placeholder': '+57 123 456789'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': 254, 'placeholder': 'correo@ejemplo.com'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if nombre:
            nombre = nombre.strip()
            if not nombre:
                raise forms.ValidationError('El nombre no puede contener solo espacios.')
            
            # Validar que no contenga solo números
            if nombre.isdigit():
                raise forms.ValidationError('El nombre no puede contener solo números.')
            
            # Validar que no contenga números
            if re.search(r'\d', nombre):
                raise forms.ValidationError('El nombre no puede contener números.')
            
            if len(nombre) < 3:
                raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
            
            if Cliente.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=nombre).exists():
                raise forms.ValidationError('Ya existe un cliente con este nombre.')
        return nombre

    def clean_documento(self):
        documento = self.cleaned_data.get('documento', '')
        if documento:
            documento = documento.strip()
            if not documento:
                raise forms.ValidationError('El documento no puede contener solo espacios.')
            
            # No permitir números negativos
            if documento.startswith('-'):
                raise forms.ValidationError('El documento no puede comenzar con un guión.')
            
            # Validar que sea alfanumérico
            if not re.match(r'^[a-zA-Z0-9\-]*$', documento):
                raise forms.ValidationError('El documento solo puede contener letras, números y guiones.')
            
            if len(documento) < 4:
                raise forms.ValidationError('El documento debe tener al menos 4 caracteres.')
            
            if len(documento) > 50:
                raise forms.ValidationError('El documento no puede exceder 50 caracteres.')
        
        return documento

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if telefono:
            telefono = telefono.strip()
            if not telefono:
                raise forms.ValidationError('El teléfono no puede contener solo espacios.')
            
            # No permitir números negativos
            if telefono[0] == '-':
                raise forms.ValidationError('El teléfono no puede comenzar con un guión (números negativos no permitidos).')
            
            # Solo dígitos, espacios, guiones, paréntesis y símbolo +
            if not re.match(r'^[+]?[(]?[\d\s\-.)]+$', telefono):
                raise forms.ValidationError('Formato de teléfono inválido. Solo se permiten dígitos, espacios, guiones, paréntesis y símbolo +.')
            
            # No permitir guiones seguidos
            if '--' in telefono:
                raise forms.ValidationError('No se permiten guiones consecutivos.')
            
            # Validar cantidad de dígitos
            num_digits = len(re.sub(r'\D', '', telefono))
            if num_digits < 7:
                raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos.')
            elif num_digits > 15:
                raise forms.ValidationError('El teléfono no puede tener más de 15 dígitos.')
        
        return telefono

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            email = email.strip()
            if not email:
                raise forms.ValidationError('El email no puede contener solo espacios.')
            
            # Validar unicidad
            if Cliente.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
                raise forms.ValidationError('Ya existe un cliente con este email.')
        
        return email

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion', '')
        if direccion:
            direccion = direccion.strip()
            if not direccion:
                raise forms.ValidationError('La dirección no puede contener solo espacios.')
            
            # No permitir que comience con guión
            if direccion.startswith('-'):
                raise forms.ValidationError('La dirección no puede comenzar con un guión.')
        
        return direccion

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        documento = cleaned_data.get('documento')
        direccion = cleaned_data.get('direccion')
        telefono = cleaned_data.get('telefono')
        email = cleaned_data.get('email')

        # Limpiar espacios en blanco al inicio y final
        if nombre:
            cleaned_data['nombre'] = nombre.strip()
        if documento:
            cleaned_data['documento'] = documento.strip()
        if direccion:
            cleaned_data['direccion'] = direccion.strip()
        if telefono:
            cleaned_data['telefono'] = telefono.strip()
        if email:
            cleaned_data['email'] = email.strip()

        # Validar que nombre sea obligatorio
        if not nombre or not nombre.strip():
            self.add_error('nombre', 'El nombre es obligatorio.')

        return cleaned_data
