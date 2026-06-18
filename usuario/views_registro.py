from django.shortcuts import render, redirect
from django.contrib import messages
from .forms_registro import RegistroClienteForm

def registro_cliente_view(request):
    if request.user.is_authenticated:
        return redirect('ventas:catalogo_cliente')
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroClienteForm()
    return render(request, 'registration/registro_cliente.html', {'form': form})
