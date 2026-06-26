from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from .models import Usuario
from django.db.models import Q
from gafra.access import ModuleAccessMixin, module_access_required

@login_required
@module_access_required('admin', module_key='usuario')
def reportes(request):
    from django.utils import timezone
    from gafra.utils_pdf import render_pdf_from_template
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '').strip()
    estado = request.GET.get('estado', '').strip()

    usuarios_qs = Usuario.objects.select_related('user').order_by('-id')
    if q:
        usuarios_qs = usuarios_qs.filter(
            Q(user__username__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__email__icontains=q)
        )
    if rol:
        usuarios_qs = usuarios_qs.filter(rol=rol)
    if estado in {'activo', 'inactivo'}:
        usuarios_qs = usuarios_qs.filter(activo=(estado == 'activo'))

    total_usuarios = usuarios_qs.count()
    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="usuarios_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'username', 'rol', 'telefono', 'activo'])
        for u in usuarios_qs[:1000]:
            writer.writerow([u.id, u.user.username, u.rol, u.telefono, u.activo])
        return resp
    if request.GET.get('export') == 'pdf':
        rows = []
        for u in usuarios_qs[:1000]:
            rows.append([
                u.id,
                u.user.username,
                u.rol,
                u.telefono,
                'Sí' if u.activo else 'No'
            ])
        context = {
            'title': 'Reporte de Usuarios',
            'subtitle': f'{len(rows)} usuarios filtrados',
            'columns': ['ID','Username','Rol','Teléfono','Activo'],
            'rows': rows,
            'ahora': timezone.now().strftime('%Y-%m-%d %H:%M'),
        }
        return render_pdf_from_template(request, 'reports/generic_report.html', context, filename='usuarios_report.pdf')
    return render(request, 'usuario/reportes.html', {
        'total_usuarios': total_usuarios,
        'q': q,
        'rol': rol,
        'estado': estado,
    })
from .forms_excel import ExcelUploadForm
import pandas as pd
from .models import Usuario
from django.contrib.auth.models import User
from gafra.utils_excel import build_excel_template_response

# --- Carga masiva desde Excel ---
@login_required
@module_access_required('admin', module_key='usuario')
def carga_masiva_usuarios(request):
    if request.method == 'GET' and request.GET.get('template') == '1':
        return build_excel_template_response(
            filename='ejemplo_usuarios.xlsx',
            columns=['username', 'password', 'rol', 'telefono', 'activo'],
            sample_rows=[
                {
                    'username': 'daniel',
                    'password': 'Gafra2026!',
                    'rol': 'admin',
                    'telefono': '3001234567',
                    'activo': True,
                },
                {
                    'username': 'thomas',
                    'password': 'Gafra2026!',
                    'rol': 'logistica',
                    'telefono': '3011234567',
                    'activo': True,
                },
            ],
        )
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                # Espera columnas: username, password, rol, telefono, activo
                for _, row in df.iterrows():
                    user, created = User.objects.get_or_create(username=row['username'])
                    if created:
                        user.set_password(row.get('password', '123456'))
                        user.save()
                    usuario, _ = Usuario.objects.update_or_create(
                        user=user,
                        defaults={
                            'rol': row.get('rol', 'cliente'),
                            'telefono': row.get('telefono', ''),
                            'activo': bool(row.get('activo', True)),
                        }
                    )
                from django.contrib import messages
                messages.success(request, 'Carga masiva completada.')
                return redirect('usuario:list')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error procesando el archivo: {e}')
    else:
        form = ExcelUploadForm()
    return render(request, 'usuario/carga_masiva.html', {'form': form})
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Usuario
from .forms import UsuarioForm


class UsuarioListView(ModuleAccessMixin, ListView):
    model = Usuario
    template_name = 'usuario/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    module_key = 'usuario'
    allowed_roles = ('admin',)

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user').order_by('-fecha_creacion', '-id')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(user__username__icontains=q)
                | Q(user__first_name__icontains=q)
                | Q(user__last_name__icontains=q)
                | Q(user__email__icontains=q)
            )
        return queryset


class UsuarioDetailView(ModuleAccessMixin, DetailView):
    model = Usuario
    template_name = 'usuario/usuario_detail.html'
    context_object_name = 'usuario_obj'
    module_key = 'usuario'
    allowed_roles = ('admin',)


class UsuarioCreateView(ModuleAccessMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuario/usuario_form.html'
    success_url = reverse_lazy('usuario:list')
    module_key = 'usuario'
    allowed_roles = ('admin',)


class UsuarioUpdateView(ModuleAccessMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuario/usuario_form.html'
    success_url = reverse_lazy('usuario:list')
    module_key = 'usuario'
    allowed_roles = ('admin',)


class UsuarioDeleteView(ModuleAccessMixin, DeleteView):
    model = Usuario
    template_name = 'usuario/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario:list')
    module_key = 'usuario'
    allowed_roles = ('admin',)


# Vistas de autenticación
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        # Verifica si el usuario tiene un rol de cliente
        try:
            usuario = Usuario.objects.get(user=request.user)
            if usuario.rol == 'logistica':
                return redirect('ventas:pedidos_logistica')
            if usuario.rol == 'cliente':
                return redirect('ventas:catalogo_cliente')
        except Usuario.DoesNotExist:
            pass
        return redirect('dashboard:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Verificar si es cliente
            try:
                usuario = Usuario.objects.get(user=user)
                if usuario.rol == 'logistica':
                    return redirect('ventas:pedidos_logistica')
                if usuario.rol == 'cliente':
                    return redirect('ventas:catalogo_cliente')
            except Usuario.DoesNotExist:
                pass
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


@login_required
def profile_view(request):
    # Mostrar plantilla según rol para evitar que clientes vean la interfaz de admin
    try:
        usuario = Usuario.objects.get(user=request.user)
        if usuario.rol == 'logistica':
            return render(request, 'registration/profile.html')
        if usuario.rol == 'cliente':
            return render(request, 'registration/profile_cliente.html')
    except Usuario.DoesNotExist:
        pass
    return render(request, 'registration/profile.html')


def become_admin(request):
    """Convierte al usuario actual en administrador"""
    if request.user.is_authenticated:
        request.user.is_staff = True
        request.user.is_superuser = True
        request.user.save()
        
        usuario, _ = Usuario.objects.get_or_create(user=request.user)
        usuario.rol = 'admin'
        usuario.save()
        
        messages.success(request, '¡Ahora eres administrador! 🎉')
    
    return redirect('dashboard:index')