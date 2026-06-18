from django.http import HttpResponse
import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms_excel import ExcelUploadForm
import pandas as pd
from .models import MateriaPrima
from proveedores.models import Proveedor

# --- Carga masiva desde Excel ---
@login_required
def carga_masiva_materias(request):
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db import models

from .models import MateriaPrima
from .forms import MateriaPrimaForm


class MateriaPrimaListView(LoginRequiredMixin, ListView):
    model = MateriaPrima
    template_name = 'inventario/inventario_list.html'
    context_object_name = 'materias_primas'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bajas = MateriaPrima.objects.filter(stock_actual__lte=models.F('stock_minimo'), activo=True)
        context['alerta_bajo_stock'] = bajas
        return context


class MateriaPrimaCreateView(LoginRequiredMixin, CreateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'inventario/inventario_form.html'
    success_url = reverse_lazy('inventario:list')


class MateriaPrimaUpdateView(LoginRequiredMixin, UpdateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'inventario/inventario_form.html'
    success_url = reverse_lazy('inventario:list')


class MateriaPrimaDeleteView(LoginRequiredMixin, DeleteView):
    model = MateriaPrima
    template_name = 'inventario/inventario_confirm_delete.html'
    success_url = reverse_lazy('inventario:list')


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
