# Reportes de productos
from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from gafra.access import ModuleAccessMixin, module_access_required


@login_required
@module_access_required('admin', 'almacenista', 'logistica', 'vendedor', module_key='productos')
def reportes(request):
    from django.utils import timezone
    from gafra.utils_pdf import render_pdf_from_template
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    estado = request.GET.get('estado', '').strip()
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    productos_qs = Producto.objects.select_related('categoria').order_by('-fecha_creacion')
    if q:
        productos_qs = productos_qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(descripcion__icontains=q))
    if categoria:
        productos_qs = productos_qs.filter(categoria__nombre__icontains=categoria)
    if estado in {'activo', 'inactivo'}:
        productos_qs = productos_qs.filter(activo=(estado == 'activo'))
    if desde:
        productos_qs = productos_qs.filter(fecha_creacion__date__gte=desde)
    if hasta:
        productos_qs = productos_qs.filter(fecha_creacion__date__lte=hasta)

    total_productos = productos_qs.count()
    productos_bajo_stock = productos_qs.filter(stock_actual__lte=5).count()
    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="productos_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'codigo', 'nombre', 'descripcion', 'categoria', 'precio_costo', 'precio_venta', 'stock_actual', 'activo', 'fecha_creacion', 'fecha_actualizacion'])
        for p in productos_qs[:1000]:
            writer.writerow([
                p.id,
                p.codigo,
                p.nombre,
                p.descripcion,
                p.categoria.nombre if p.categoria else '',
                p.precio_costo,
                p.precio_venta,
                p.stock_actual,
                p.activo,
                p.fecha_creacion.strftime('%Y-%m-%d %H:%M'),
                p.fecha_actualizacion.strftime('%Y-%m-%d %H:%M'),
            ])
        return resp
    if request.GET.get('export') == 'pdf':
        rows = []
        for p in productos_qs[:1000]:
            rows.append([
                p.id,
                p.codigo,
                p.nombre,
                (p.descripcion or '')[:140],
                p.categoria.nombre if p.categoria else '',
                f"{p.precio_costo}",
                f"{p.precio_venta}",
                p.stock_actual,
                'Sí' if p.activo else 'No',
                p.fecha_creacion.strftime('%Y-%m-%d %H:%M') if p.fecha_creacion else '',
            ])
        context = {
            'title': 'Reporte de Productos',
            'subtitle': f'{len(rows)} productos filtrados',
            'columns': ['ID','Código','Nombre','Descripción','Categoría','Precio costo','Precio venta','Stock','Activo','Fecha creación'],
            'rows': rows,
            'ahora': timezone.now().strftime('%Y-%m-%d %H:%M'),
        }
        return render_pdf_from_template(request, 'reports/generic_report.html', context, filename='productos_report.pdf')
    return render(request, 'productos/reportes.html', {
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'q': q,
        'categoria': categoria,
        'estado': estado,
        'desde': desde or '',
        'hasta': hasta or '',
    })
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .models import Producto
from .forms import ProductoForm, IngredienteRecetaFormSet


class ProductoListView(ModuleAccessMixin, ListView):
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 20
    module_key = 'productos'
    allowed_roles = ('admin', 'almacenista', 'logistica', 'vendedor')

    def get_queryset(self):
        queryset = super().get_queryset().select_related('categoria').order_by('nombre', 'id')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(categoria__nombre__icontains=q)
            )
        return queryset



from .models import Receta


class ProductoDetailView(ModuleAccessMixin, DetailView):
    model = Producto
    template_name = 'productos/producto_detail.html'
    context_object_name = 'producto'
    module_key = 'productos'
    allowed_roles = ('admin', 'almacenista', 'logistica', 'vendedor')

class ProductoCreateView(ModuleAccessMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:list')
    module_key = 'productos'
    allowed_roles = ('admin', 'almacenista', 'logistica', 'vendedor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingrediente_formset'] = IngredienteRecetaFormSet(self.request.POST)
        else:
            context['ingrediente_formset'] = IngredienteRecetaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ingrediente_formset = context['ingrediente_formset']
        if ingrediente_formset.is_valid():
            self.object = form.save()
            # Crear la receta asociada
            receta, created = Receta.objects.get_or_create(producto=self.object)
            ingrediente_formset.instance = receta
            ingrediente_formset.save()
            messages.success(self.request, 'Producto creado correctamente.')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)



class ProductoUpdateView(ModuleAccessMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('productos:list')
    module_key = 'productos'
    allowed_roles = ('admin', 'almacenista', 'logistica', 'vendedor')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receta, created = Receta.objects.get_or_create(producto=self.object)
        if self.request.POST:
            context['ingrediente_formset'] = IngredienteRecetaFormSet(self.request.POST, instance=receta)
        else:
            context['ingrediente_formset'] = IngredienteRecetaFormSet(instance=receta)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ingrediente_formset = context['ingrediente_formset']
        if ingrediente_formset.is_valid():
            self.object = form.save()
            receta, created = Receta.objects.get_or_create(producto=self.object)
            ingrediente_formset.instance = receta
            ingrediente_formset.save()
            messages.success(self.request, 'Producto guardado correctamente.')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ProductoDeleteView(ModuleAccessMixin, DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('productos:list')
    module_key = 'productos'
    allowed_roles = ('admin', 'almacenista', 'logistica', 'vendedor')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f'Producto "{obj}" eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


# --- Carga masiva desde Excel ---
from django.shortcuts import render, redirect
from .forms_excel import ExcelUploadForm
import pandas as pd
from .models import Producto, Categoria

@login_required
@module_access_required('admin', 'almacenista', 'logistica', 'vendedor', module_key='productos')
def carga_masiva_productos(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                # Espera columnas: nombre, descripcion, categoria, precio_costo, precio_venta, stock_actual, activo
                for _, row in df.iterrows():
                    categoria, _ = Categoria.objects.get_or_create(nombre=row.get('categoria', 'Sin categoría'))
                    Producto.objects.update_or_create(
                        nombre=row['nombre'],
                        defaults={
                            'descripcion': row.get('descripcion', ''),
                            'categoria': categoria,
                            'precio_costo': row.get('precio_costo', 0),
                            'precio_venta': row.get('precio_venta', 0),
                            'stock_actual': row.get('stock_actual', 0),
                            'activo': bool(row.get('activo', True)),
                        }
                    )
                messages.success(request, 'Carga masiva completada.')
                return redirect('productos:list')
            except Exception as e:
                messages.error(request, f'Error procesando el archivo: {e}')
    else:
        form = ExcelUploadForm()
    return render(request, 'productos/carga_masiva.html', {'form': form})

