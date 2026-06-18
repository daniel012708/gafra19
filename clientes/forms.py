from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'minlength': 3, 'maxlength': 150, 'placeholder': 'Nombre completo'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 255}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 20}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': 254}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if Cliente.objects.exclude(pk=self.instance.pk).filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe un cliente con este nombre.')
        return nombre

    def clean_documento(self):
        documento = self.cleaned_data.get('documento', '').strip()
        if documento and len(documento) < 4:
            raise forms.ValidationError('El documento debe tener al menos 4 caracteres.')
        return documento

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono and (len(telefono) < 7 or len(telefono) > 20):
            raise forms.ValidationError('El teléfono debe tener entre 7 y 20 dígitos.')
        return telefono
