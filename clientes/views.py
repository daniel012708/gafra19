from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms_excel import ExcelUploadForm
import pandas as pd
from .models import Cliente
from django.db.models import Q

# --- Carga masiva desde Excel ---
from gafra.access import ModuleAccessMixin, module_access_required


@login_required
@module_access_required('admin', 'vendedor', module_key='clientes')
def carga_masiva_clientes(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                # Espera columnas: nombre, documento, direccion, telefono, email
                for _, row in df.iterrows():
                    Cliente.objects.update_or_create(
                        nombre=row['nombre'],
                        defaults={
                            'documento': row.get('documento', ''),
                            'direccion': row.get('direccion', ''),
                            'telefono': row.get('telefono', ''),
                            'email': row.get('email', ''),
                        }
                    )
                from django.contrib import messages
                messages.success(request, 'Carga masiva completada.')
                return redirect('clientes:list')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error procesando el archivo: {e}')
    else:
        form = ExcelUploadForm()
    return render(request, 'clientes/carga_masiva.html', {'form': form})
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Cliente
from .forms import ClienteForm


class ClienteListView(ModuleAccessMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 20
    module_key = 'clientes'
    allowed_roles = ('admin', 'vendedor')

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-fecha_registro', '-id')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(documento__icontains=q)
                | Q(email__icontains=q)
                | Q(telefono__icontains=q)
            )
        return queryset


class ClienteDetailView(ModuleAccessMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'
    module_key = 'clientes'
    allowed_roles = ('admin', 'vendedor')


class ClienteCreateView(ModuleAccessMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:list')
    module_key = 'clientes'
    allowed_roles = ('admin', 'vendedor')


class ClienteUpdateView(ModuleAccessMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:list')
    module_key = 'clientes'
    allowed_roles = ('admin', 'vendedor')


class ClienteDeleteView(ModuleAccessMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:list')
    module_key = 'clientes'
    allowed_roles = ('admin', 'vendedor')


@login_required
@module_access_required('admin', 'vendedor', module_key='clientes')
def reportes(request):
    """Reportes simples para clientes."""
    from django.http import HttpResponse
    import csv
    from django.utils import timezone
    from gafra.utils_pdf import render_pdf_from_template
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    clientes_qs = Cliente.objects.order_by('-fecha_registro')
    if q:
        clientes_qs = clientes_qs.filter(
            Q(nombre__icontains=q) | Q(documento__icontains=q) | Q(email__icontains=q)
        )
    if desde:
        clientes_qs = clientes_qs.filter(fecha_registro__date__gte=desde)
    if hasta:
        clientes_qs = clientes_qs.filter(fecha_registro__date__lte=hasta)

    total_clientes = clientes_qs.count()

    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="clientes_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'nombre', 'documento', 'direccion', 'telefono', 'email', 'fecha_registro'])
        for c in clientes_qs[:1000]:
            writer.writerow([
                c.id,
                c.nombre,
                c.documento,
                c.direccion,
                c.telefono,
                c.email,
                c.fecha_registro.isoformat() if c.fecha_registro else ''
            ])
        return resp

    if request.GET.get('export') == 'pdf':
        rows = []
        for c in clientes_qs[:1000]:
            rows.append([
                c.id,
                c.nombre,
                c.documento,
                c.direccion,
                c.telefono,
                c.email,
                c.fecha_registro.isoformat() if c.fecha_registro else ''
            ])
        context = {
            'title': 'Reporte de Clientes',
            'subtitle': f'{len(rows)} clientes filtrados',
            'columns': ['ID', 'Nombre', 'Documento', 'Dirección', 'Teléfono', 'Email', 'Fecha registro'],
            'rows': rows,
            'ahora': timezone.now().strftime('%Y-%m-%d %H:%M'),
        }
        return render_pdf_from_template(request, 'reports/generic_report.html', context, filename='clientes_report.pdf')

    return render(request, 'clientes/reportes.html', {
        'total_clientes': total_clientes,
        'q': q,
        'desde': desde or '',
        'hasta': hasta or '',
    })
