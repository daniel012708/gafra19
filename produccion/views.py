from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from .models import OrdenProduccion
from django.db.models import Q
from gafra.access import ModuleAccessMixin, module_access_required

@login_required
@module_access_required('admin', 'logistica', module_key='produccion')
def reportes(request):
    total_ordenes = OrdenProduccion.objects.count()
    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="produccion_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'producto', 'cantidad_a_producir', 'estado', 'responsable', 'fecha_creacion'])
        for o in OrdenProduccion.objects.select_related('producto', 'responsable').order_by('-fecha_creacion')[:1000]:
            writer.writerow([
                o.id,
                o.producto.nombre if o.producto else '',
                o.cantidad_a_producir,
                o.estado,
                o.responsable.username if o.responsable else '',
                o.fecha_creacion.strftime('%Y-%m-%d %H:%M')
            ])
        return resp
    return render(request, 'produccion/reportes.html', {'total_ordenes': total_ordenes})
from .forms_excel import ExcelUploadForm
import pandas as pd
from .models import OrdenProduccion
from productos.models import Producto, Receta
from django.contrib.auth.models import User

# --- Carga masiva desde Excel ---
@login_required
def carga_masiva_ordenes(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                # Espera columnas: producto, receta, cantidad_a_producir, estado, responsable, notas
                for _, row in df.iterrows():
                    producto = Producto.objects.filter(nombre=row['producto']).first()
                    receta = None
                    if producto:
                        receta = Receta.objects.filter(producto=producto).first()
                    responsable = None
                    if 'responsable' in row and row['responsable']:
                        responsable = User.objects.filter(username=row['responsable']).first()
                    if producto and receta:
                        OrdenProduccion.objects.create(
                            producto=producto,
                            receta=receta,
                            cantidad_a_producir=row.get('cantidad_a_producir', 1),
                            estado=row.get('estado', 'pendiente'),
                            responsable=responsable,
                            notas=row.get('notas', ''),
                        )
                from django.contrib import messages
                messages.success(request, 'Carga masiva completada.')
                return redirect('produccion:list')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error procesando el archivo: {e}')
    else:
        form = ExcelUploadForm()
    return render(request, 'produccion/carga_masiva.html', {'form': form})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils import timezone
from django.db import transaction

from .models import OrdenProduccion, ProduccionDiaria
from .forms import OrdenProduccionForm, ProduccionDiariaForm


class OrdenProduccionListView(ModuleAccessMixin, ListView):
    model = OrdenProduccion
    template_name = 'produccion/produccion_list.html'
    context_object_name = 'ordenes_produccion'
    paginate_by = 20
    module_key = 'produccion'
    allowed_roles = ('admin', 'logistica')

    def get_queryset(self):
        queryset = super().get_queryset().select_related('producto', 'receta', 'responsable')
        estado = self.request.GET.get('estado')
        q = self.request.GET.get('q', '').strip()
        if estado:
            queryset = queryset.filter(estado=estado)
        if q:
            queryset = queryset.filter(
                Q(producto__nombre__icontains=q)
                | Q(responsable__username__icontains=q)
                | Q(notas__icontains=q)
            )
        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar conteo de órdenes en progreso para la alerta
        context['ordenes_en_progreso_count'] = OrdenProduccion.objects.filter(estado='en_progreso').count()
        return context


class OrdenProduccionDetailView(ModuleAccessMixin, DetailView):
    model = OrdenProduccion
    template_name = 'produccion/produccion_detail.html'
    context_object_name = 'orden'
    module_key = 'produccion'
    allowed_roles = ('admin', 'logistica')


@login_required
@module_access_required('admin', 'logistica', module_key='produccion')
def orden_produccion_create(request):
    if request.method == 'POST':
        form = OrdenProduccionForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.responsable = request.user
            # Asignar automáticamente la receta del producto
            orden.receta = orden.producto.receta

            # Verificar si hay suficientes materias primas
            if not orden.puede_iniciar():
                messages.error(request, 'No hay suficientes materias primas para iniciar esta producción.')
                return render(request, 'produccion/produccion_form.html', {'form': form})

            orden.save()
            messages.success(request, f'Orden de producción {orden.id} creada exitosamente.')
            return redirect('produccion:list')
    else:
        form = OrdenProduccionForm()
    return render(request, 'produccion/produccion_form.html', {'form': form})


@login_required
@module_access_required('admin', 'logistica', module_key='produccion')
def orden_produccion_iniciar(request, pk):
    orden = get_object_or_404(OrdenProduccion, pk=pk)

    if orden.estado != 'pendiente':
        messages.error(request, 'Esta orden ya ha sido iniciada.')
        return redirect('produccion:list')

    if not orden.puede_iniciar():
        messages.error(request, 'No hay suficientes materias primas para iniciar esta producción.')
        return redirect('produccion:list')

    with transaction.atomic():
        orden.estado = 'en_progreso'
        orden.fecha_inicio = timezone.now()
        orden.responsable = request.user
        orden.consumir_materias_primas()
        orden.save()

    messages.success(request, f'Producción de {orden.producto.nombre} iniciada. Materias primas consumidas.')
    return redirect('produccion:list')


@login_required
@module_access_required('admin', 'logistica', module_key='produccion')
def orden_produccion_completar(request, pk):
    orden = get_object_or_404(OrdenProduccion, pk=pk)

    if orden.estado != 'en_progreso':
        messages.error(request, 'Esta orden no está en progreso.')
        return redirect('produccion:list')

    if request.method == 'POST':
        form = ProduccionDiariaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                produccion_diaria = form.save(commit=False)
                produccion_diaria.orden_produccion = orden
                produccion_diaria.responsable = request.user
                # Asignar fecha automáticamente si no viene del form
                if not produccion_diaria.fecha:
                    from django.utils import timezone
                    produccion_diaria.fecha = timezone.now().date()
                produccion_diaria.save()

                # Completar la orden
                orden.estado = 'completada'
                orden.fecha_fin = timezone.now()
                orden.producir_productos()
                orden.save()

            messages.success(request, f'Producción completada. {orden.cantidad_a_producir} unidades de {orden.producto.nombre} agregadas al inventario.')
            return redirect('produccion:list')
    else:
        form = ProduccionDiariaForm()

    # Preparar datos de ingredientes con cantidades calculadas
    ingredientes_data = []
    for ingrediente in orden.receta.ingredientes.all():
        cantidad_total = ingrediente.cantidad_requerida * orden.cantidad_a_producir
        ingredientes_data.append({
            'materia_prima': ingrediente.materia_prima,
            'cantidad_requerida': ingrediente.cantidad_requerida,
            'cantidad_total': cantidad_total
        })

    return render(request, 'produccion/orden_produccion_completar.html', {
        'orden': orden,
        'form': form,
        'ingredientes': ingredientes_data
    })


class OrdenProduccionCreateView(ModuleAccessMixin, CreateView):
    model = OrdenProduccion
    form_class = OrdenProduccionForm
    template_name = 'produccion/produccion_form.html'
    success_url = reverse_lazy('produccion:list')
    module_key = 'produccion'
    allowed_roles = ('admin', 'logistica')

    def form_valid(self, form):
        form.instance.responsable = self.request.user
        # Asignar automáticamente la receta del producto
        form.instance.receta = form.instance.producto.receta
        messages.success(self.request, f'Orden de producción creada exitosamente.')
        return super().form_valid(form)


class OrdenProduccionUpdateView(ModuleAccessMixin, UpdateView):
    model = OrdenProduccion
    form_class = OrdenProduccionForm
    template_name = 'produccion/produccion_form.html'
    success_url = reverse_lazy('produccion:list')
    module_key = 'produccion'
    allowed_roles = ('admin', 'logistica')

    def form_valid(self, form):
        # Asignar automáticamente la receta del producto
        form.instance.receta = form.instance.producto.receta
        messages.success(self.request, f'Orden de producción actualizada exitosamente.')
        return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset().filter(estado='pendiente')


class OrdenProduccionDeleteView(ModuleAccessMixin, DeleteView):
    model = OrdenProduccion
    template_name = 'produccion/produccion_confirm_delete.html'
    success_url = reverse_lazy('produccion:list')
    module_key = 'produccion'
    allowed_roles = ('admin', 'logistica')

    def get_queryset(self):
        return super().get_queryset().filter(estado='pendiente')


def reportes(request):
    """Reportes simples para producción."""
    from django.http import HttpResponse
    import csv

    from django.utils import timezone
    from gafra.utils_pdf import render_pdf_from_template
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    responsable = request.GET.get('responsable', '').strip()
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    ordenes_qs = OrdenProduccion.objects.select_related('producto', 'responsable').order_by('-fecha_creacion')
    if q:
        ordenes_qs = ordenes_qs.filter(Q(producto__nombre__icontains=q) | Q(receta__descripcion__icontains=q))
    if estado:
        ordenes_qs = ordenes_qs.filter(estado=estado)
    if responsable:
        ordenes_qs = ordenes_qs.filter(responsable__username__icontains=responsable)
    if desde:
        ordenes_qs = ordenes_qs.filter(fecha_creacion__date__gte=desde)
    if hasta:
        ordenes_qs = ordenes_qs.filter(fecha_creacion__date__lte=hasta)

    total_ordenes = ordenes_qs.count()
    en_progreso = ordenes_qs.filter(estado='en_progreso').count()

    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="produccion_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'producto', 'cantidad_a_producir', 'estado', 'responsable', 'fecha_creacion', 'fecha_inicio', 'fecha_fin'])
        for o in ordenes_qs[:1000]:
            writer.writerow([
                o.id,
                o.producto.nombre if o.producto else '',
                o.cantidad_a_producir,
                o.estado,
                o.responsable.username if o.responsable else '',
                o.fecha_creacion.strftime('%Y-%m-%d %H:%M') if o.fecha_creacion else '',
                o.fecha_inicio.strftime('%Y-%m-%d %H:%M') if o.fecha_inicio else '',
                o.fecha_fin.strftime('%Y-%m-%d %H:%M') if o.fecha_fin else '',
            ])
        return resp

    if request.GET.get('export') == 'pdf':
        qs = ordenes_qs[:1000]
        rows = []
        for o in qs:
            rows.append({
                'ID': o.id,
                'Producto': o.producto.nombre if o.producto else '',
                'Cantidad': o.cantidad_a_producir,
                'Estado': o.estado,
                'Responsable': o.responsable.username if o.responsable else '',
                'Fecha creación': o.fecha_creacion.isoformat() if o.fecha_creacion else ''
            })

        total = ordenes_qs.count()
        total_completadas = ordenes_qs.filter(estado__icontains='complet').count()
        total_pendientes = ordenes_qs.filter(estado__icontains='pendient').count()

        # Small human-friendly description summary
        description = (
            f'Total registros consultados: {len(rows)}. ' \
            f'Total en sistema: {total}. ' \
            f'Completadas: {total_completadas}. Pendientes: {total_pendientes}.'
        )

        context = {
            'title': 'Reporte de Producción',
            'columns': ['ID','Producto','Cantidad','Estado','Responsable','Fecha creación'],
            'rows': rows,
            'description': description,
            'total_records': len(rows),
            'total_completadas': total_completadas,
            'total_pendientes': total_pendientes,
            'meta': {
                'Consulta': 'Últimas órdenes',
                'Generado': timezone.now().strftime('%Y-%m-%d %H:%M')
            }
        }

        return render_pdf_from_template(request, 'reports/pro_report.html', context, filename='produccion_report.pdf')

    return render(request, 'produccion/reportes.html', {
        'total_ordenes': total_ordenes,
        'en_progreso': en_progreso,
        'q': q,
        'estado': estado,
        'responsable': responsable,
        'desde': desde or '',
        'hasta': hasta or '',
    })
