from django.http import HttpResponse
import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms_excel import ExcelUploadForm
import pandas as pd
from .models import Proveedor
from gafra.access import ModuleAccessMixin, module_access_required
from gafra.utils_excel import build_excel_template_response

# --- Carga masiva desde Excel ---
@login_required
@module_access_required('admin', 'almacenista', 'logistica', module_key='proveedores')
def carga_masiva_proveedores(request):
    if request.method == 'GET' and request.GET.get('template') == '1':
        return build_excel_template_response(
            filename='ejemplo_proveedores.xlsx',
            columns=['nombre', 'razon_social', 'rfc', 'contacto', 'telefono', 'email', 'direccion', 'ciudad', 'estado', 'pais', 'codigo_postal', 'tipo', 'sitio_web', 'activo'],
            sample_rows=[
                {
                    'nombre': 'Maderas Andinas',
                    'razon_social': 'Maderas Andinas SAS',
                    'rfc': 'GFR000000001',
                    'contacto': 'Andrea Torres',
                    'telefono': '3154567890',
                    'email': 'ventas@maderasandinas.com',
                    'direccion': 'Calle 80 # 25-40',
                    'ciudad': 'Bogota',
                    'estado': 'Bogota',
                    'pais': 'Colombia',
                    'codigo_postal': '110111',
                    'tipo': 'Nacional',
                    'sitio_web': 'https://maderasandinas.com',
                    'activo': True,
                },
                {
                    'nombre': 'Textiles Nido',
                    'razon_social': 'Textiles Nido SAS',
                    'rfc': 'GFR000000002',
                    'contacto': 'Camilo Rojas',
                    'telefono': '3185678901',
                    'email': 'contacto@textilesnido.com',
                    'direccion': 'Carrera 32 # 10-22',
                    'ciudad': 'Medellin',
                    'estado': 'Antioquia',
                    'pais': 'Colombia',
                    'codigo_postal': '050021',
                    'tipo': 'Nacional',
                    'sitio_web': 'https://textilesnido.com',
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
                # Espera columnas: nombre, razon_social, rfc, contacto, telefono, email, direccion, ciudad, estado, pais, codigo_postal, tipo, sitio_web, activo
                for _, row in df.iterrows():
                    Proveedor.objects.update_or_create(
                        nombre=row['nombre'],
                        defaults={
                            'razon_social': row.get('razon_social', ''),
                            'rfc': row.get('rfc', ''),
                            'contacto': row.get('contacto', ''),
                            'telefono': row.get('telefono', ''),
                            'email': row.get('email', ''),
                            'direccion': row.get('direccion', ''),
                            'ciudad': row.get('ciudad', ''),
                            'estado': row.get('estado', ''),
                            'pais': row.get('pais', ''),
                            'codigo_postal': row.get('codigo_postal', ''),
                            'tipo': row.get('tipo', 'Nacional'),
                            'sitio_web': row.get('sitio_web', ''),
                            'activo': bool(row.get('activo', True)),
                        }
                    )
                from django.contrib import messages
                messages.success(request, 'Carga masiva completada.')
                return redirect('proveedores:list')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error procesando el archivo: {e}')
    else:
        form = ExcelUploadForm()
    return render(request, 'proveedores/carga_masiva.html', {'form': form})
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Proveedor
from .forms import ProveedorForm
from .movimientos import ProveedorMovimiento


class ProveedorListView(ModuleAccessMixin, ListView):
    model = Proveedor
    template_name = 'proveedores/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 20
    module_key = 'proveedores'
    allowed_roles = ('admin', 'almacenista', 'logistica')

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nombre', 'id')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(contacto__icontains=q)
                | Q(email__icontains=q)
                | Q(ciudad__icontains=q)
            )
        return queryset


class ProveedorDetailView(ModuleAccessMixin, DetailView):
    model = Proveedor
    template_name = 'proveedores/proveedor_detail.html'
    context_object_name = 'proveedor'
    module_key = 'proveedores'
    allowed_roles = ('admin', 'almacenista', 'logistica')



class ProveedorCreateView(ModuleAccessMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedores:list')
    module_key = 'proveedores'
    allowed_roles = ('admin', 'almacenista', 'logistica')

    def form_valid(self, form):
        response = super().form_valid(form)
        ProveedorMovimiento.objects.create(
            proveedor=self.object,
            usuario=self.request.user,
            accion='CREADO',
            detalles=f"Proveedor creado: {self.object.nombre}"
        )
        return response



class ProveedorUpdateView(ModuleAccessMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedores/proveedor_form.html'
    success_url = reverse_lazy('proveedores:list')
    module_key = 'proveedores'
    allowed_roles = ('admin', 'almacenista', 'logistica')

    def form_valid(self, form):
        response = super().form_valid(form)
        ProveedorMovimiento.objects.create(
            proveedor=self.object,
            usuario=self.request.user,
            accion='EDITADO',
            detalles=f"Proveedor editado: {self.object.nombre}"
        )
        return response



class ProveedorDeleteView(ModuleAccessMixin, DeleteView):
    model = Proveedor
    template_name = 'proveedores/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedores:list')
    module_key = 'proveedores'
    allowed_roles = ('admin', 'almacenista', 'logistica')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        ProveedorMovimiento.objects.create(
            proveedor=self.object,
            usuario=self.request.user,
            accion='ELIMINADO',
            detalles=f"Proveedor eliminado: {self.object.nombre}"
        )
        return super().delete(request, *args, **kwargs)


@login_required
@module_access_required('admin', 'almacenista', 'logistica', module_key='proveedores')
def reportes(request):
    from django.utils import timezone
    from gafra.utils_pdf import render_pdf_from_template
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    estado = request.GET.get('estado', '').strip()
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    proveedores_qs = Proveedor.objects.order_by('-id')
    if q:
        proveedores_qs = proveedores_qs.filter(Q(nombre__icontains=q) | Q(razon_social__icontains=q) | Q(rfc__icontains=q))
    if tipo:
        proveedores_qs = proveedores_qs.filter(tipo=tipo)
    if estado in {'activo', 'inactivo'}:
        proveedores_qs = proveedores_qs.filter(activo=(estado == 'activo'))
    if desde:
        proveedores_qs = proveedores_qs.filter(fecha_creacion__date__gte=desde)
    if hasta:
        proveedores_qs = proveedores_qs.filter(fecha_creacion__date__lte=hasta)

    total_proveedores = proveedores_qs.count()
    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="proveedores_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'nombre', 'razon_social', 'rfc', 'contacto', 'telefono', 'email', 'direccion', 'ciudad', 'estado', 'pais', 'codigo_postal', 'tipo', 'sitio_web', 'activo'])
        for p in proveedores_qs[:1000]:
            writer.writerow([
                p.id,
                p.nombre,
                p.razon_social,
                p.rfc,
                p.contacto,
                p.telefono,
                p.email,
                p.direccion,
                p.ciudad,
                p.estado,
                p.pais,
                p.codigo_postal,
                p.tipo,
                p.sitio_web,
                p.activo
            ])
        return resp
    if request.GET.get('export') == 'pdf':
        rows = []
        for p in proveedores_qs[:1000]:
            rows.append([
                p.id,
                p.nombre,
                p.razon_social,
                p.rfc,
                p.contacto,
                p.telefono,
                p.email,
                p.direccion,
                p.ciudad,
                p.estado,
                p.pais,
                p.codigo_postal,
                p.tipo,
                p.sitio_web,
                'Sí' if p.activo else 'No'
            ])
        context = {
            'title': 'Reporte de Proveedores',
            'subtitle': f'{len(rows)} proveedores filtrados',
            'columns': ['ID','Nombre','Razón social','RFC','Contacto','Teléfono','Email','Dirección','Ciudad','Estado','País','CP','Tipo','Web','Activo'],
            'rows': rows,
            'ahora': timezone.now().strftime('%Y-%m-%d %H:%M'),
        }
        return render_pdf_from_template(request, 'reports/generic_report.html', context, filename='proveedores_report.pdf')
    return render(request, 'proveedores/reportes.html', {
        'total_proveedores': total_proveedores,
        'q': q,
        'tipo': tipo,
        'estado': estado,
        'desde': desde or '',
        'hasta': hasta or '',
    })
