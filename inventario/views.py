from django.http import HttpResponse
import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms_excel import ExcelUploadForm
import pandas as pd
from .models import MateriaPrima
from proveedores.models import Proveedor
from gafra.access import ModuleAccessMixin, module_access_required
from gafra.utils_excel import build_excel_template_response

# --- Carga masiva desde Excel ---
@login_required
@module_access_required('admin', 'almacenista', 'logistica', module_key='inventario')
def carga_masiva_materias(request):
    if request.method == 'GET' and request.GET.get('template') == '1':
        return build_excel_template_response(
            filename='ejemplo_materias.xlsx',
            columns=['nombre', 'descripcion', 'marca', 'proveedor', 'precio_unitario', 'unidad_medida', 'stock_actual', 'stock_minimo', 'ubicacion', 'observaciones', 'activo'],
            sample_rows=[
                {
                    'nombre': 'Espuma de alta densidad',
                    'descripcion': 'Espuma para colchonetas linea premium',
                    'marca': 'FoamKids',
                    'proveedor': 'GAFRA DEMO PROV 01 - Maderas Andinas',
                    'precio_unitario': 38.50,
                    'unidad_medida': 'kg',
                    'stock_actual': 680,
                    'stock_minimo': 150,
                    'ubicacion': 'Bodega-1-A2',
                    'observaciones': 'Uso para colchonetas y protectores',
                    'activo': True,
                },
                {
                    'nombre': 'Tubos metalicos',
                    'descripcion': 'Tubo estructural para corrales',
                    'marca': 'MetalBaby',
                    'proveedor': 'GAFRA DEMO PROV 04 - Metal Kids Industrial',
                    'precio_unitario': 29.50,
                    'unidad_medida': 'm',
                    'stock_actual': 540,
                    'stock_minimo': 120,
                    'ubicacion': 'Bodega-2-B1',
                    'observaciones': 'Corte por orden de produccion',
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
                # Espera columnas: nombre, descripcion, marca, proveedor, precio_unitario, unidad_medida, stock_actual, stock_minimo, ubicacion, observaciones, activo
                for _, row in df.iterrows():
                    proveedor, _ = Proveedor.objects.get_or_create(nombre=row.get('proveedor', 'Proveedor demo'))
                    MateriaPrima.objects.update_or_create(
                        nombre=row['nombre'],
                        defaults={
                            'descripcion': row.get('descripcion', ''),
                            'marca': row.get('marca', ''),
                            'proveedor': proveedor,
                            'precio_unitario': row.get('precio_unitario', 0),
                            'unidad_medida': row.get('unidad_medida', 'pz'),
                            'stock_actual': row.get('stock_actual', 0),
                            'stock_minimo': row.get('stock_minimo', 0),
                            'ubicacion': row.get('ubicacion', ''),
                            'observaciones': row.get('observaciones', ''),
                            'activo': bool(row.get('activo', True)),
                        }
                    )
                from django.contrib import messages
                messages.success(request, 'Carga masiva completada.')
                return redirect('inventario:list')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error procesando el archivo: {e}')
    else:
        form = ExcelUploadForm()
    return render(request, 'inventario/carga_masiva.html', {'form': form})

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db import models

from .models import MateriaPrima
from .forms import MateriaPrimaForm


class MateriaPrimaListView(ModuleAccessMixin, ListView):
    model = MateriaPrima
    template_name = 'inventario/inventario_list.html'
    context_object_name = 'materias_primas'
    paginate_by = 20
    module_key = 'inventario'
    allowed_roles = ('admin', 'almacenista', 'logistica')

    def get_queryset(self):
        queryset = super().get_queryset().select_related('proveedor').order_by('nombre', 'id')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(codigo__icontains=q)
                | Q(marca__icontains=q)
                | Q(proveedor__nombre__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bajas = MateriaPrima.objects.filter(stock_actual__lte=models.F('stock_minimo'), activo=True)
        context['alerta_bajo_stock'] = bajas
        return context


class MateriaPrimaDetailView(ModuleAccessMixin, DetailView):
    model = MateriaPrima
    template_name = 'inventario/inventario_detail.html'
    context_object_name = 'materia'
    module_key = 'inventario'
    allowed_roles = ('admin', 'almacenista', 'logistica')


class MateriaPrimaCreateView(ModuleAccessMixin, CreateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'inventario/inventario_form.html'
    success_url = reverse_lazy('inventario:list')
    module_key = 'inventario'
    allowed_roles = ('admin', 'almacenista', 'logistica')


class MateriaPrimaUpdateView(ModuleAccessMixin, UpdateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'inventario/inventario_form.html'
    success_url = reverse_lazy('inventario:list')
    module_key = 'inventario'
    allowed_roles = ('admin', 'almacenista', 'logistica')


class MateriaPrimaDeleteView(ModuleAccessMixin, DeleteView):
    model = MateriaPrima
    template_name = 'inventario/inventario_confirm_delete.html'
    success_url = reverse_lazy('inventario:list')
    module_key = 'inventario'
    allowed_roles = ('admin', 'almacenista', 'logistica')


@login_required
@module_access_required('admin', 'almacenista', 'logistica', module_key='inventario')
def reportes(request):
    from django.utils import timezone
    from gafra.utils_pdf import render_pdf_from_template
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    proveedor = request.GET.get('proveedor', '').strip()
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    materias_qs = MateriaPrima.objects.select_related('proveedor').order_by('-fecha_creacion')
    if q:
        materias_qs = materias_qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(marca__icontains=q))
    if estado in {'activo', 'inactivo'}:
        materias_qs = materias_qs.filter(activo=(estado == 'activo'))
    if proveedor:
        materias_qs = materias_qs.filter(proveedor__nombre__icontains=proveedor)
    if desde:
        materias_qs = materias_qs.filter(fecha_creacion__date__gte=desde)
    if hasta:
        materias_qs = materias_qs.filter(fecha_creacion__date__lte=hasta)

    total_materias = materias_qs.count()
    bajo_stock = materias_qs.filter(stock_actual__lte=models.F('stock_minimo')).count()
    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="inventario_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'codigo', 'nombre', 'descripcion', 'marca', 'proveedor', 'precio_unitario', 'unidad_medida', 'stock_actual', 'stock_minimo', 'ubicacion', 'observaciones', 'activo'])
        for m in materias_qs[:1000]:
            writer.writerow([
                m.id,
                m.codigo,
                m.nombre,
                m.descripcion,
                m.marca,
                m.proveedor.nombre if m.proveedor else '',
                m.precio_unitario,
                m.unidad_medida,
                m.stock_actual,
                m.stock_minimo,
                m.ubicacion,
                m.observaciones,
                m.activo
            ])
        return resp
    if request.GET.get('export') == 'pdf':
        rows = []
        for m in materias_qs[:1000]:
            rows.append([
                m.id,
                m.codigo,
                m.nombre,
                (m.descripcion or '')[:120],
                m.marca,
                m.proveedor.nombre if m.proveedor else '',
                f"{m.precio_unitario}",
                m.unidad_medida,
                m.stock_actual,
                m.stock_minimo,
                m.ubicacion or '',
                'Sí' if m.activo else 'No'
            ])
        context = {
            'title': 'Reporte de Inventario',
            'subtitle': f'{len(rows)} materias primas filtradas',
            'columns': ['ID','Código','Nombre','Descripción','Marca','Proveedor','Precio unit.','Unidad','Stock','Stock mínimo','Ubicación','Activo'],
            'rows': rows,
            'ahora': timezone.now().strftime('%Y-%m-%d %H:%M'),
        }
        return render_pdf_from_template(request, 'reports/generic_report.html', context, filename='inventario_report.pdf')
    return render(request, 'inventario/reportes.html', {
        'total_materias': total_materias,
        'bajo_stock': bajo_stock,
        'q': q,
        'estado': estado,
        'proveedor': proveedor,
        'desde': desde or '',
        'hasta': hasta or '',
    })
