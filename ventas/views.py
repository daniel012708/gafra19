from django.http import HttpResponse
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from gafra.utils_pdf import render_pdf_from_template
from gafra.soft_delete import SoftDeleteMixin
from gafra.access import user_has_role
from .models import Venta

from datetime import datetime, timedelta
from django.contrib.auth.models import User


def reportes(request):
    # Filters
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    usuario = request.GET.get('usuario')
    estado = request.GET.get('estado')

    ventas_qs = Venta.objects.select_related('cliente', 'vendedor').order_by('-fecha')
    if desde:
        try:
            d = datetime.strptime(desde, '%Y-%m-%d')
            ventas_qs = ventas_qs.filter(fecha__gte=d)
        except Exception:
            pass
    if hasta:
        try:
            h = datetime.strptime(hasta, '%Y-%m-%d') + timedelta(days=1)
            ventas_qs = ventas_qs.filter(fecha__lt=h)
        except Exception:
            pass
    if usuario:
        ventas_qs = ventas_qs.filter(vendedor__username=usuario)
    if estado:
        ventas_qs = ventas_qs.filter(estado=estado)

    total_ventas = ventas_qs.count()
    total_ingresos = ventas_qs.aggregate(total=Sum('total'))['total'] or 0

    if request.GET.get('export') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="ventas_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['id', 'numero_venta', 'cliente', 'vendedor', 'estado', 'total', 'fecha', 'fecha_completado'])
        for v in ventas_qs[:1000]:
            writer.writerow([
                v.id,
                v.numero_venta,
                v.cliente.nombre if v.cliente else '',
                v.vendedor.username if v.vendedor else '',
                v.estado,
                v.total,
                v.fecha.strftime('%Y-%m-%d %H:%M'),
                v.fecha_completado.strftime('%Y-%m-%d %H:%M') if v.fecha_completado else '',
            ])
        return resp
    # Generate small chart (sales per day) to embed in UI and PDF.
    # If matplotlib is unavailable in an environment (e.g. lightweight deploy),
    # return None so the app keeps working and only the chart is skipped.
    def make_sales_chart(qs):
        try:
            import io
            import base64
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
        except Exception:
            return None

        # aggregate by date
        from django.db.models.functions import TruncDate
        daily = qs.annotate(day=TruncDate('fecha')).values('day').annotate(total=Sum('total')).order_by('day')
        days = [r['day'].strftime('%Y-%m-%d') for r in daily]
        totals = [float(r['total'] or 0) for r in daily]
        if not days:
            days = []
            totals = []
        fig, ax = plt.subplots(figsize=(8,2.5))
        ax.plot(days, totals, marker='o', color='#60a5fa')
        ax.fill_between(days, totals, color='#60a5fa', alpha=0.12)
        ax.set_title('Ventas por día')
        ax.set_ylabel('Monto')
        ax.set_xlabel('Fecha')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150)
        plt.close(fig)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('ascii')
        return f'data:image/png;base64,{img_b64}'

    chart_img = make_sales_chart(ventas_qs[:1000])

    # Si piden PDF, generar reporte estilizado
    if request.GET.get('export') == 'pdf':
        ventas_list = []
        for v in ventas_qs[:1000]:
            ventas_list.append({
                'id': v.id,
                'fecha': v.fecha.strftime('%Y-%m-%d %H:%M'),
                'cliente_nombre': v.cliente.nombre if v.cliente else '',
                'vendedor': v.vendedor.get_full_name() if v.vendedor else '',
                'estado': v.estado,
                'total': f"{v.total:.2f}",
            })
        total_ing = ventas_qs.aggregate(total=Sum('total'))['total'] or 0
        context = {
            'ventas': ventas_list,
            'total_ventas': ventas_qs.count(),
            'total_ingresos': f"{total_ing:.2f}",
            'clientes_unicos': ventas_qs.values('cliente').distinct().count(),
            'fecha_inicio': desde or '—',
            'fecha_fin': hasta or '—',
            'ahora': timezone.now().strftime('%Y-%m-%d %H:%M'),
            'usuario': request.user.username if request.user.is_authenticated else 'anon',
            'chart_img': chart_img,
        }
        return render_pdf_from_template(request, 'reports/ventas_report.html', context, filename='ventas_report.pdf')

    # Render UI with filters, chart preview and export buttons
    usuarios = User.objects.all()[:200]
    return render(request, 'ventas/reportes.html', {
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'chart_img': chart_img,
        'desde': desde or '',
        'hasta': hasta or '',
        'usuario_filter': usuario or '',
        'estado_filter': estado or '',
        'usuarios': usuarios,
    })


@login_required
def logistica_pedidos(request):
    if not user_has_role(request.user, 'logistica', 'admin'):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard:index')

    pedidos = (
        Venta.objects.select_related('cliente', 'vendedor')
        .prefetch_related('detalles__producto')
        .filter(estado__in=['pendiente', 'en_progreso'])
        .order_by('fecha')
    )
    estado = request.GET.get('estado')
    cliente = request.GET.get('cliente')
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    q = request.GET.get('q', '').strip()

    if estado in {'pendiente', 'en_progreso'}:
        pedidos = pedidos.filter(estado=estado)
    if cliente:
        pedidos = pedidos.filter(cliente__nombre__icontains=cliente)
    if fecha_desde:
        pedidos = pedidos.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        pedidos = pedidos.filter(fecha__date__lte=fecha_hasta)
    if q:
        pedidos = pedidos.filter(numero_venta__icontains=q)

    return render(request, 'ventas/logistica_pedidos.html', {
        'pedidos': pedidos,
        'filtros': {
            'estado': estado or '',
            'cliente': cliente or '',
            'desde': fecha_desde or '',
            'hasta': fecha_hasta or '',
            'q': q,
        },
    })


@login_required
def completar_pedido_logistica(request, pk):
    if not user_has_role(request.user, 'logistica', 'admin'):
        messages.error(request, 'No tienes permisos para completar pedidos.')
        return redirect('dashboard:index')

    pedido = get_object_or_404(Venta.objects.select_related('cliente', 'vendedor'), pk=pk)
    if pedido.estado not in {'pendiente', 'en_progreso'}:
        messages.warning(request, 'Solo se pueden completar pedidos pendientes o en proceso.')
        return redirect('ventas:pedidos_logistica')

    if request.method == 'POST':
        pedido.estado = 'completada'
        pedido.fecha_completado = timezone.now()
        pedido.save(update_fields=['estado', 'fecha_completado'])
        messages.success(request, f'Pedido {pedido.numero_venta} marcado como completado.')
        return redirect('ventas:pedidos_logistica')

    return render(request, 'ventas/completar_pedido_logistica.html', {'pedido': pedido})
from .forms_excel import ExcelUploadForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from .models import Venta
from clientes.models import Cliente
from django.contrib.auth.models import User

# --- Carga masiva desde Excel ---
@login_required
def carga_masiva_ventas(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                # Espera columnas: cliente, vendedor, estado, descuento, impuesto, total, observaciones
                for _, row in df.iterrows():
                    cliente = None
                    if 'cliente' in row and row['cliente']:
                        cliente, _ = Cliente.objects.get_or_create(nombre=row['cliente'])
                    vendedor = None
                    if 'vendedor' in row and row['vendedor']:
                        vendedor = User.objects.filter(username=row['vendedor']).first()
                    Venta.objects.create(
                        cliente=cliente,
                        vendedor=vendedor,
                        estado=row.get('estado', 'pendiente'),
                        descuento=row.get('descuento', 0),
                        impuesto=row.get('impuesto', 0),
                        total=row.get('total', 0),
                        observaciones=row.get('observaciones', ''),
                    )
                from django.contrib import messages
                messages.success(request, 'Carga masiva completada.')
                return redirect('ventas:lista')
            except Exception as e:
                from django.contrib import messages
                messages.error(request, f'Error procesando el archivo: {e}')
    else:
        form = ExcelUploadForm()
    return render(request, 'ventas/carga_masiva.html', {'form': form})
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
import logging

logger = logging.getLogger(__name__)


# Catálogo para clientes: lista productos activos con filtros simples
@never_cache
@ensure_csrf_cookie
def catalogo_cliente(request):
    from productos.models import Producto, Categoria
    from .models import Favorito, Carrito

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    precio_max = request.GET.get('precio_max', '')

    productos_qs = Producto.objects.filter(activo=True)

    if q:
        productos_qs = productos_qs.filter(nombre__icontains=q)
    if categoria:
        try:
            productos_qs = productos_qs.filter(categoria_id=int(categoria))
        except Exception:
            pass
    if precio_max:
        try:
            productos_qs = productos_qs.filter(precio_venta__lte=float(precio_max))
        except Exception:
            pass

    categorias = Categoria.objects.all()

    paginator = Paginator(productos_qs, 12)
    page = request.GET.get('page', 1)
    productos = paginator.get_page(page)

    favoritos_ids = []
    carrito = None
    if request.user.is_authenticated:
        favoritos_ids = list(Favorito.objects.filter(usuario=request.user).values_list('producto_id', flat=True))
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': q,
        'categoria_seleccionada': categoria,
        'precio_max': precio_max,
        'favoritos_ids': favoritos_ids,
        'carrito': carrito,
        'is_paginated': productos.has_other_pages(),
        'page_obj': productos,
    }

    return render(request, 'ventas/catalogo_cliente.html', context)


@never_cache
@ensure_csrf_cookie
def catalogo_publico(request):
    """Versión pública del catálogo que permite explorar y agregar al carrito (usa sesión para usuarios anónimos)."""
    from productos.models import Producto, Categoria

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    precio_max = request.GET.get('precio_max', '')

    productos_qs = Producto.objects.filter(activo=True)

    if q:
        productos_qs = productos_qs.filter(nombre__icontains=q)
    if categoria:
        try:
            productos_qs = productos_qs.filter(categoria_id=int(categoria))
        except Exception:
            pass
    if precio_max:
        try:
            productos_qs = productos_qs.filter(precio_venta__lte=float(precio_max))
        except Exception:
            pass

    categorias = Categoria.objects.all()

    paginator = Paginator(productos_qs, 12)
    page = request.GET.get('page', 1)
    productos = paginator.get_page(page)

    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': q,
        'categoria_seleccionada': categoria,
        'precio_max': precio_max,
        'is_paginated': productos.has_other_pages(),
        'page_obj': productos,
        # Indica a la plantilla que esta es la versión pública
        'publico': True,
    }

    return render(request, 'ventas/catalogo_cliente.html', context)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.urls import reverse_lazy
from django.forms.models import modelformset_factory
from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.shortcuts import redirect, render
from .forms import DetalleFormset, VentaForm
from .models import Venta, DetalleVenta

# Vista para eliminar una venta
class VentaDeleteView(SoftDeleteMixin, LoginRequiredMixin, DeleteView):
    model = Venta
    template_name = 'ventas/venta_confirm_delete.html'
    success_url = reverse_lazy('ventas:lista')

# Vista de detalle para una venta
class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from productos.models import Producto
from clientes.models import Cliente
from .models import Venta
from django.contrib import messages

@login_required
def nueva_venta(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        cantidades = {}
        for key, value in request.POST.items():
            if key.startswith('cantidad_'):
                try:
                    pk = int(key.replace('cantidad_', ''))
                    cantidad = int(value)
                    if cantidad > 0:
                        cantidades[pk] = cantidad
                except Exception:
                    pass
        if not cliente_id or not cantidades:
            messages.error(request, 'Selecciona un cliente y al menos un producto con cantidad mayor a 0.')
            productos = Producto.objects.filter(activo=True)
            clientes = Cliente.objects.all()
            return render(request, 'ventas/venta_form.html', {'productos': productos, 'clientes': clientes, 'cliente_id': cliente_id, 'cantidades': cantidades})
        # Guardar en sesión para la confirmación
        request.session['venta_cliente'] = cliente_id
        request.session['venta_cantidades'] = cantidades
        return redirect('ventas:confirmar')
    else:
        productos = Producto.objects.filter(activo=True)
        clientes = Cliente.objects.all()
        return render(request, 'ventas/venta_form.html', {'productos': productos, 'clientes': clientes})

from django.views import View



from django.views.decorators.http import require_http_methods
@login_required
@require_http_methods(["GET", "POST"])
def confirmar_venta(request):
    from productos.models import Producto
    from clientes.models import Cliente
    if request.method == 'POST':
        cliente_id = request.session.get('venta_cliente')
        cantidades = request.session.get('venta_cantidades', {})
        if not cliente_id or not cantidades:
            return redirect('ventas:crear')
        cliente = Cliente.objects.get(pk=cliente_id)
        total = 0
        venta = Venta.objects.create(
            cliente=cliente,
            vendedor=request.user,
            estado='completada',
            total=0,
        )
        for pk_str, cantidad in cantidades.items():
            try:
                pk = int(pk_str)
                cantidad = int(cantidad)
                if cantidad > 0:
                    producto = Producto.objects.get(pk=pk)
                    precio = float(producto.precio_venta)
                    subtotal = precio * cantidad
                    from .models import DetalleVenta
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        subtotal=subtotal,
                    )
                    producto.stock_actual -= cantidad
                    producto.save()
                    total += subtotal
            except Exception:
                pass
        venta.total = total
        venta.save()
        # Limpiar sesión
        request.session.pop('venta_cliente', None)
        request.session.pop('venta_cantidades', None)
        return redirect('ventas:detalle', pk=venta.pk)
    else:
        cliente_id = request.session.get('venta_cliente')
        cantidades = request.session.get('venta_cantidades', {})
        if not cliente_id or not cantidades:
            return redirect('ventas:crear')
        cliente = Cliente.objects.get(pk=cliente_id)
        productos = Producto.objects.filter(pk__in=[int(pk) for pk in cantidades.keys()])
        detalles = []
        total = 0
        for producto in productos:
            cantidad = int(cantidades.get(str(producto.pk), 0))
            if cantidad > 0:
                precio = float(producto.precio_venta)
                subtotal = precio * cantidad
                detalles.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal
                })
                total += subtotal
        return render(request, 'ventas/venta_confirmar.html', {
            'cliente': cliente,
            'detalles': detalles,
            'total': total,
        })

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)


# Catálogo para clientes: lista productos activos con filtros simples
def catalogo_cliente(request):
    from productos.models import Producto, Categoria
    from .models import Favorito, Carrito

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    precio_max = request.GET.get('precio_max', '')

    productos_qs = Producto.objects.filter(activo=True)

    if q:
        productos_qs = productos_qs.filter(nombre__icontains=q)
    if categoria:
        try:
            productos_qs = productos_qs.filter(categoria_id=int(categoria))
        except Exception:
            pass
    if precio_max:
        try:
            productos_qs = productos_qs.filter(precio_venta__lte=float(precio_max))
        except Exception:
            pass

    categorias = Categoria.objects.all()

    paginator = Paginator(productos_qs, 12)
    page = request.GET.get('page', 1)
    productos = paginator.get_page(page)

    favoritos_ids = []
    carrito = None
    if request.user.is_authenticated:
        favoritos_ids = list(Favorito.objects.filter(usuario=request.user).values_list('producto_id', flat=True))
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': q,
        'categoria_seleccionada': categoria,
        'precio_max': precio_max,
        'favoritos_ids': favoritos_ids,
        'carrito': carrito,
        'is_paginated': productos.has_other_pages(),
        'page_obj': productos,
    }

    return render(request, 'ventas/catalogo_cliente.html', context)


def catalogo_publico(request):
    """Versión pública del catálogo que permite explorar y agregar al carrito (usa sesión para usuarios anónimos)."""
    from productos.models import Producto, Categoria

    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    precio_max = request.GET.get('precio_max', '')

    productos_qs = Producto.objects.filter(activo=True)

    if q:
        productos_qs = productos_qs.filter(nombre__icontains=q)
    if categoria:
        try:
            productos_qs = productos_qs.filter(categoria_id=int(categoria))
        except Exception:
            pass
    if precio_max:
        try:
            productos_qs = productos_qs.filter(precio_venta__lte=float(precio_max))
        except Exception:
            pass

    categorias = Categoria.objects.all()

    paginator = Paginator(productos_qs, 12)
    page = request.GET.get('page', 1)
    productos = paginator.get_page(page)

    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': q,
        'categoria_seleccionada': categoria,
        'precio_max': precio_max,
        'is_paginated': productos.has_other_pages(),
        'page_obj': productos,
        # Indica a la plantilla que esta es la versión pública
        'publico': True,
    }

    return render(request, 'ventas/catalogo_cliente.html', context)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.urls import reverse_lazy
from django.forms.models import modelformset_factory
from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.shortcuts import redirect, render
from .forms import DetalleFormset, VentaForm
from .models import Venta, DetalleVenta

# Vista para eliminar una venta
class VentaDeleteView(SoftDeleteMixin, LoginRequiredMixin, DeleteView):
    model = Venta
    template_name = 'ventas/venta_confirm_delete.html'
    success_url = reverse_lazy('ventas:lista')

# Vista de detalle para una venta
class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'
class VentaWizardView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = DetalleFormset(self.request.POST)
        else:
            data['detalles'] = DetalleFormset()
        from productos.models import Producto
        productos = Producto.objects.all()
        data['productos_precios'] = {str(p.id): str(p.precio_venta) for p in productos}
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        # Guardar datos en sesión y redirigir a confirmación
        # Convertir cualquier instancia de modelo / decimal / datetime a un tipo JSON-serializable
        from django.db.models import Model
        from decimal import Decimal
        from datetime import date, datetime

        venta_form_serializable = {}
        for key, val in form.cleaned_data.items():
            if isinstance(val, Model):
                venta_form_serializable[key] = val.pk
            elif isinstance(val, Decimal):
                venta_form_serializable[key] = str(val)
            elif isinstance(val, (date, datetime)):
                venta_form_serializable[key] = val.isoformat()
            else:
                venta_form_serializable[key] = val

        self.request.session['venta_form'] = venta_form_serializable
        detalles_data = []
        # Validar formset antes de usar cleaned_data
        if not detalles.is_valid():
            # Re-renderizar la página con errores del formset
            return self.render_to_response(self.get_context_data(form=form))

        for ddata in detalles.cleaned_data:
            if ddata and not ddata.get('DELETE', False):
                detalles_data.append({
                    'producto': ddata['producto'].id,
                    'cantidad': ddata['cantidad'],
                })
        self.request.session['venta_detalles'] = detalles_data
        return redirect('ventas:confirmar')

from django.views import View


class VentaConfirmarView(LoginRequiredMixin, View):
    template_name = 'ventas/venta_confirmar.html'

    def get(self, request):
        venta_form = request.session.get('venta_form')
        detalles_data = request.session.get('venta_detalles', [])

        if not venta_form:
            return redirect('ventas:crear')  # evita error

        from productos.models import Producto
        from clientes.models import Cliente

        cliente = Cliente.objects.get(pk=venta_form['cliente'])

        detalles = []
        total = 0

        for d in detalles_data:
            producto = Producto.objects.get(id=d['producto'])
            cantidad = int(d['cantidad'])
            precio = float(producto.precio_venta)
            subtotal = precio * cantidad

            detalles.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio,
                'subtotal': subtotal
            })

            total += subtotal

        return render(request, self.template_name, {
            'cliente': cliente,
            'detalles': detalles,
            'total': total,
        })

    def post(self, request):
        """Crear la venta usando los datos guardados en sesión."""
        venta_form = request.session.get('venta_form')
        detalles_data = request.session.get('venta_detalles', [])

        if not venta_form:
            return redirect('ventas:crear')

        from clientes.models import Cliente
        from productos.models import Producto

        cliente = Cliente.objects.get(pk=venta_form['cliente'])

        # Crear la venta
        venta = Venta.objects.create(
            cliente=cliente,
            vendedor=request.user,
            estado=venta_form.get('estado', 'pendiente'),
            total=0,
        )

        total = 0
        for d in detalles_data:
            producto = Producto.objects.get(id=d['producto'])
            cantidad = int(d['cantidad'])
            precio = float(producto.precio_venta)
            subtotal = precio * cantidad

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal,
            )

            # Actualizar stock si existe el campo
            try:
                producto.stock_actual -= cantidad
                producto.save()
            except Exception:
                pass

            total += subtotal

        venta.total = total
        venta.save()

        # Limpiar sesión
        request.session.pop('venta_form', None)
        request.session.pop('venta_detalles', None)

        return redirect('ventas:detalle', pk=venta.pk)


def reportes(request):
    """Reportes simples para ventas: métricas y exportar CSV."""
    from django.db.models import Sum, Q
    import csv
    from django.http import HttpResponse
    from datetime import datetime, timedelta

    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    usuario = request.GET.get('usuario')
    estado = request.GET.get('estado')
    q = request.GET.get('q', '').strip()

    ventas_qs = Venta.objects.select_related('cliente', 'vendedor').order_by('-fecha')
    if desde:
        try:
            ventas_qs = ventas_qs.filter(fecha__gte=datetime.strptime(desde, '%Y-%m-%d'))
        except Exception:
            pass
    if hasta:
        try:
            ventas_qs = ventas_qs.filter(fecha__lt=datetime.strptime(hasta, '%Y-%m-%d') + timedelta(days=1))
        except Exception:
            pass
    if usuario:
        ventas_qs = ventas_qs.filter(vendedor__username=usuario)
    if estado:
        ventas_qs = ventas_qs.filter(estado=estado)
    if q:
        ventas_qs = ventas_qs.filter(
            Q(numero_venta__icontains=q) |
            Q(cliente__nombre__icontains=q) |
            Q(vendedor__username__icontains=q)
        )

    total_ventas = ventas_qs.count()
    total_ingresos = ventas_qs.aggregate(total=Sum('total'))['total'] or 0

    if request.GET.get('export') == 'csv':
        # Exportar ventas a CSV
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="ventas_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['numero_venta', 'fecha', 'cliente', 'vendedor', 'estado', 'total'])
        for v in ventas_qs[:1000]:
            writer.writerow([
                v.numero_venta,
                v.fecha.isoformat(),
                v.cliente.nombre if v.cliente else '',
                v.vendedor.username if v.vendedor else '',
                v.estado,
                str(v.total),
            ])
        return resp

    context = {
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'desde': desde or '',
        'hasta': hasta or '',
        'usuario_filter': usuario or '',
        'estado_filter': estado or '',
        'q': q,
        'usuarios': User.objects.all().order_by('username'),
    }
    return render(request, 'ventas/reportes.html', context)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.forms import inlineformset_factory
from django.contrib import messages

from .models import Venta, DetalleVenta
from .forms import VentaForm


DetalleFormset = inlineformset_factory(
    Venta, DetalleVenta,
    fields=['producto', 'cantidad', 'precio_unitario', 'subtotal'],
    extra=1, can_delete=True
)


class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'vendedor')
        estado = self.request.GET.get('estado')
        q = self.request.GET.get('q', '').strip()
        if estado:
            queryset = queryset.filter(estado=estado)
        if q:
            queryset = queryset.filter(numero_venta__icontains=q)
        return queryset.order_by('-fecha')


class VentaCreateView(LoginRequiredMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:lista')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = DetalleFormset(self.request.POST)
        else:
            data['detalles'] = DetalleFormset()
        # Agregar dict de precios de productos para el JS
        from productos.models import Producto
        productos = Producto.objects.all()
        data['productos_precios'] = {str(p.id): str(p.precio_venta) for p in productos}
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        # Asignar un total temporal para evitar IntegrityError
        form.instance.total = 0
        self.object = form.save()
        if detalles.is_valid():
            detalles.instance = self.object
            detalles_instances = detalles.save(commit=False)
            for di in detalles_instances:
                try:
                    di.subtotal = di.cantidad * di.precio_unitario
                except Exception:
                    pass
                di.venta = self.object
                di.save()
            for obj in detalles.deleted_objects:
                obj.delete()
            try:
                self.object.recompute_total()
            except Exception:
                pass
        return super().form_valid(form)


class VentaUpdateView(LoginRequiredMixin, UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:lista')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['detalles'] = DetalleFormset(self.request.POST, instance=self.object)
        else:
            data['detalles'] = DetalleFormset(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        detalles = context['detalles']
        self.object = form.save()
        if detalles.is_valid():
            detalles.instance = self.object
            detalles_instances = detalles.save(commit=False)
            for di in detalles_instances:
                try:
                    di.subtotal = di.cantidad * di.precio_unitario
                except Exception:
                    pass
                di.venta = self.object
                di.save()
            for obj in detalles.deleted_objects:
                obj.delete()
            try:
                self.object.recompute_total()
            except Exception:
                pass
        return super().form_valid(form)


## Vista original deshabilitada por el nuevo flujo de dos pasos
# class VentaCreateView(LoginRequiredMixin, CreateView):
#     ...
## Código eliminado por error de indentación y estar fuera de contexto
## Código eliminado por error de sintaxis y estar fuera de contexto


def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito"""
    # importar modelos localmente para evitar NameError si el módulo cambia
    from productos.models import Producto
    from .models import Carrito, ItemCarrito

    # Aceptar POST por defecto; permitir GET con parámetro ?cantidad= para pruebas/uso directo
    producto = get_object_or_404(Producto, id=producto_id, activo=True)

    if request.method == 'POST':
        fuente = request.POST
    else:
        fuente = request.GET

    try:
        cantidad = int(fuente.get('cantidad', 1))
    except Exception:
        cantidad = 1

    # Debug logging para diagnosticar problemas en producción local
    try:
        logger.debug(f"agregar_al_carrito: user={request.user} method={request.method} producto_id={producto_id} cantidad={cantidad}")
    except Exception:
        pass
    
    # Verificar disponibilidad
    if cantidad > producto.stock_actual:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'No hay suficiente stock'}, status=400)
        messages.error(request, f"Solo hay {producto.stock_actual} unidades disponibles")
        return redirect('ventas:catalogo_cliente')
    
    # Si el usuario está autenticado, usar el modelo Carrito; si no, usar la sesión
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        # Agregar o actualizar item en el carrito persistente
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad}
        )

        if not created:
            item.cantidad += cantidad
            item.save()
    else:
        # Carrito en sesión: lista de dicts {'producto': id, 'cantidad': n}
        session_cart = request.session.get('session_cart', [])
        # buscar si ya existe
        found = False
        for it in session_cart:
            if it.get('producto') == producto.id:
                it['cantidad'] = int(it.get('cantidad', 0)) + cantidad
                found = True
                break
        if not found:
            session_cart.append({'producto': producto.id, 'cantidad': cantidad})
        request.session['session_cart'] = session_cart
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': carrito.items.count() if request.user.is_authenticated else len(request.session.get('session_cart', [])),
            'message': f'{producto.nombre} agregado al carrito'
        })
    
    messages.success(request, f'{producto.nombre} agregado al carrito')
    return redirect('ventas:ver_carrito')


@login_required
def ver_carrito(request):
    """Muestra el carrito del cliente"""
    from .models import Carrito
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        items = carrito.items.all()
        total = carrito.total()
    else:
        # Construir items desde la sesión
        from productos.models import Producto
        session_cart = request.session.get('session_cart', [])
        items = []
        total = 0
        for it in session_cart:
            try:
                producto = Producto.objects.get(id=it.get('producto'))
            except Producto.DoesNotExist:
                continue
            cantidad = int(it.get('cantidad', 1))
            class PseudoItem:
                pass
            pi = PseudoItem()
            pi.producto = producto
            pi.cantidad = cantidad
            pi.id = None
            try:
                pi.subtotal = producto.precio_venta * cantidad
            except Exception:
                pi.subtotal = producto.precio_venta
            items.append(pi)
            try:
                total += float(pi.subtotal)
            except Exception:
                pass

        carrito = None

    context = {
        'carrito': carrito,
        'items': items,
        'total': total,
    }
    return render(request, 'ventas/ver_carrito.html', context)


@login_required
def actualizar_cantidad_carrito(request, item_id):
    """Actualiza la cantidad de un item en el carrito"""
    from .models import ItemCarrito, Carrito

    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)

    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad <= 0:
        item.delete()
    else:
        # Verificar disponibilidad
        if cantidad > item.producto.stock_actual:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': f'Solo hay {item.producto.stock_actual} unidades disponibles'}, status=400)
            messages.error(request, f"Solo hay {item.producto.stock_actual} unidades disponibles")
        else:
            item.cantidad = cantidad
            item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        carrito = item.carrito if cantidad > 0 else Carrito.objects.get(usuario=request.user)
        return JsonResponse({
            'success': True,
            'total': str(carrito.total()),
            'total_items': carrito.items.count(),
        })
    
    return redirect('ventas:ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    """Elimina un item del carrito"""
    from .models import ItemCarrito, Carrito

    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        carrito = Carrito.objects.get(usuario=request.user)
        return JsonResponse({
            'success': True,
            'total_items': carrito.items.count(),
            'total': str(carrito.total()),
        })
    
    messages.success(request, 'Producto removido del carrito')
    return redirect('ventas:ver_carrito')


@login_required
def agregar_favorito(request, producto_id):
    """Agrega un producto a favoritos"""
    from productos.models import Producto
    from .models import Favorito

    producto = get_object_or_404(Producto, id=producto_id)

    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        producto=producto
    )
    
    if not created:
        favorito.delete()
        mensaje = f'{producto.nombre} eliminado de favoritos'
        is_favorite = False
    else:
        mensaje = f'{producto.nombre} agregado a favoritos'
        is_favorite = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': mensaje
        })
    
    messages.success(request, mensaje)
    return redirect('ventas:catalogo_cliente')


@login_required
def ver_favoritos(request):
    """Muestra los productos favoritos del cliente"""
    from .models import Favorito, Carrito

    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto')
    productos = [fav.producto for fav in favoritos]
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    favoritos_ids = list(Favorito.objects.filter(usuario=request.user).values_list('producto_id', flat=True))
    
    context = {
        'productos': productos,
        'favoritos': True,
        'carrito': carrito,
        'total_items': carrito.items.count(),
        'favoritos_ids': favoritos_ids,
    }
    return render(request, 'ventas/favoritos.html', context)


@login_required
def checkout(request):
    """Procesa el checkout del carrito"""
    # Forzar login antes de procesar el pago
    if not request.user.is_authenticated:
        return redirect('login')

    from .models import Carrito
    from clientes.models import Cliente

    # Si había un carrito en sesión (usuario venía anónimo), migrarlo al carrito del usuario
    session_cart = request.session.pop('session_cart', None)
    if session_cart:
        from .models import Carrito, ItemCarrito
        from productos.models import Producto

        carrito_obj, _ = Carrito.objects.get_or_create(usuario=request.user)
        for it in session_cart:
            prod_id = it.get('producto')
            cantidad = int(it.get('cantidad', 1))
            try:
                producto = Producto.objects.get(id=prod_id)
            except Producto.DoesNotExist:
                continue
            item_obj, created = ItemCarrito.objects.get_or_create(carrito=carrito_obj, producto=producto, defaults={'cantidad': cantidad})
            if not created:
                item_obj.cantidad += cantidad
                item_obj.save()

    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.all()
    
    if not items:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('ventas:catalogo_cliente')
    
    if request.method == 'POST':
        # Crear venta
        try:
            # Obtener o crear cliente para este usuario
            cliente, _ = Cliente.objects.get_or_create(
                email=request.user.email,
                defaults={
                    'nombre': request.user.get_full_name() or request.user.username,
                    'telefono': request.POST.get('telefono', ''),
                    'direccion': request.POST.get('direccion', ''),
                }
            )
            
            # Crear la venta
            venta = Venta.objects.create(
                cliente=cliente,
                vendedor=request.user,  # El cliente es también el "vendedor" de su propia orden
                estado='pendiente',
                total=carrito.total()
            )
            
            # Crear detalles de venta
            total = 0
            for item in items:
                # Verificar stock
                if item.cantidad > item.producto.stock_actual:
                    venta.delete()
                    messages.error(request, f'No hay suficiente stock de {item.producto.nombre}')
                    return redirect('ventas:ver_carrito')
                
                detalle = DetalleVenta.objects.create(
                    venta=venta,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio_venta,
                    subtotal=item.subtotal()
                )
                total += detalle.subtotal
                
                # Actualizar stock
                item.producto.stock_actual -= item.cantidad
                item.producto.save()
            
            # Actualizar total de venta
            venta.total = total
            venta.save()
            
            # Limpiar carrito
            items.delete()
            
            messages.success(request, f'¡Pedido #{venta.numero_venta} creado exitosamente!')
            return redirect('ventas:detalle_pedido', pk=venta.pk)
        
        except Exception as e:
            messages.error(request, f'Error al procesar el pedido: {str(e)}')
            return redirect('ventas:ver_carrito')
    
    context = {
        'carrito': carrito,
        'items': items,
        'total': carrito.total(),
    }
    return render(request, 'ventas/checkout.html', context)


@login_required
def historial_pedidos(request):
    """Muestra el historial de pedidos del cliente"""
    # Obtener ventas donde el usuario autenticado es el que las compró (cliente)
    from clientes.models import Cliente

    cliente = Cliente.objects.filter(email=request.user.email).first()
    
    if cliente:
        pedidos = Venta.objects.filter(cliente=cliente).prefetch_related('detalles')
    else:
        pedidos = Venta.objects.none()
    
    # Ordenar por fecha descendente
    pedidos = pedidos.order_by('-fecha')
    
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'ventas/historial_pedidos.html', context)


@login_required
def detalle_pedido(request, pk):
    """Muestra los detalles de un pedido"""
    pedido = get_object_or_404(Venta, pk=pk)
    
    # Permitir acceso al cliente dueño o al rol logístico/administrativo.
    if not user_has_role(request.user, 'admin', 'logistica') and pedido.cliente and pedido.cliente.email != request.user.email:
        messages.error(request, 'No tienes permiso para ver este pedido')
        return redirect('ventas:historial_pedidos')
    
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all(),
    }
    template_name = 'ventas/detalle_pedido_logistica.html' if user_has_role(request.user, 'admin', 'logistica') else 'ventas/detalle_pedido.html'
    return render(request, template_name, context)



@login_required
def ver_carrito(request):
    """Muestra el carrito del cliente"""
    from .models import Carrito
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        items = carrito.items.all()
        total = carrito.total()
    else:
        # Construir items desde la sesión
        from productos.models import Producto
        session_cart = request.session.get('session_cart', [])
        items = []
        total = 0
        for it in session_cart:
            try:
                producto = Producto.objects.get(id=it.get('producto'))
            except Producto.DoesNotExist:
                continue
            cantidad = int(it.get('cantidad', 1))
            class PseudoItem:
                pass
            pi = PseudoItem()
            pi.producto = producto
            pi.cantidad = cantidad
            pi.id = None
            try:
                pi.subtotal = producto.precio_venta * cantidad
            except Exception:
                pi.subtotal = producto.precio_venta
            items.append(pi)
            try:
                total += float(pi.subtotal)
            except Exception:
                pass

        carrito = None

    context = {
        'carrito': carrito,
        'items': items,
        'total': total,
    }
    return render(request, 'ventas/ver_carrito.html', context)


@login_required
def actualizar_cantidad_carrito(request, item_id):
    """Actualiza la cantidad de un item en el carrito"""
    from .models import ItemCarrito, Carrito

    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)

    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad <= 0:
        item.delete()
    else:
        # Verificar disponibilidad
        if cantidad > item.producto.stock_actual:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': f'Solo hay {item.producto.stock_actual} unidades disponibles'}, status=400)
            messages.error(request, f"Solo hay {item.producto.stock_actual} unidades disponibles")
        else:
            item.cantidad = cantidad
            item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        carrito = item.carrito if cantidad > 0 else Carrito.objects.get(usuario=request.user)
        return JsonResponse({
            'success': True,
            'total': str(carrito.total()),
            'total_items': carrito.items.count(),
        })
    
    return redirect('ventas:ver_carrito')


@login_required
def eliminar_del_carrito(request, item_id):
    """Elimina un item del carrito"""
    from .models import ItemCarrito, Carrito

    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        carrito = Carrito.objects.get(usuario=request.user)
        return JsonResponse({
            'success': True,
            'total_items': carrito.items.count(),
            'total': str(carrito.total()),
        })
    
    messages.success(request, 'Producto removido del carrito')
    return redirect('ventas:ver_carrito')


@login_required
def agregar_favorito(request, producto_id):
    """Agrega un producto a favoritos"""
    from productos.models import Producto
    from .models import Favorito

    producto = get_object_or_404(Producto, id=producto_id)

    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        producto=producto
    )
    
    if not created:
        favorito.delete()
        mensaje = f'{producto.nombre} eliminado de favoritos'
        is_favorite = False
    else:
        mensaje = f'{producto.nombre} agregado a favoritos'
        is_favorite = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': mensaje
        })
    
    messages.success(request, mensaje)
    return redirect('ventas:catalogo_cliente')


@login_required
def ver_favoritos(request):
    """Muestra los productos favoritos del cliente"""
    from .models import Favorito, Carrito

    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto')
    productos = [fav.producto for fav in favoritos]
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    favoritos_ids = list(Favorito.objects.filter(usuario=request.user).values_list('producto_id', flat=True))
    
    context = {
        'productos': productos,
        'favoritos': True,
        'carrito': carrito,
        'total_items': carrito.items.count(),
        'favoritos_ids': favoritos_ids,
    }
    return render(request, 'ventas/favoritos.html', context)


@login_required
def checkout(request):
    """Procesa el checkout del carrito"""
    # Forzar login antes de procesar el pago
    if not request.user.is_authenticated:
        return redirect('login')

    from .models import Carrito
    from clientes.models import Cliente

    # Si había un carrito en sesión (usuario venía anónimo), migrarlo al carrito del usuario
    session_cart = request.session.pop('session_cart', None)
    if session_cart:
        from .models import Carrito, ItemCarrito
        from productos.models import Producto

        carrito_obj, _ = Carrito.objects.get_or_create(usuario=request.user)
        for it in session_cart:
            prod_id = it.get('producto')
            cantidad = int(it.get('cantidad', 1))
            try:
                producto = Producto.objects.get(id=prod_id)
            except Producto.DoesNotExist:
                continue
            item_obj, created = ItemCarrito.objects.get_or_create(carrito=carrito_obj, producto=producto, defaults={'cantidad': cantidad})
            if not created:
                item_obj.cantidad += cantidad
                item_obj.save()

    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.all()
    
    if not items:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('ventas:catalogo_cliente')
    
    if request.method == 'POST':
        # Crear venta
        try:
            # Obtener o crear cliente para este usuario
            cliente, _ = Cliente.objects.get_or_create(
                email=request.user.email,
                defaults={
                    'nombre': request.user.get_full_name() or request.user.username,
                    'telefono': request.POST.get('telefono', ''),
                    'direccion': request.POST.get('direccion', ''),
                }
            )
            
            # Crear la venta
            venta = Venta.objects.create(
                cliente=cliente,
                vendedor=request.user,  # El cliente es también el "vendedor" de su propia orden
                estado='pendiente',
                total=carrito.total()
            )
            
            # Crear detalles de venta
            total = 0
            for item in items:
                # Verificar stock
                if item.cantidad > item.producto.stock_actual:
                    venta.delete()
                    messages.error(request, f'No hay suficiente stock de {item.producto.nombre}')
                    return redirect('ventas:ver_carrito')
                
                detalle = DetalleVenta.objects.create(
                    venta=venta,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio_venta,
                    subtotal=item.subtotal()
                )
                total += detalle.subtotal
                
                # Actualizar stock
                item.producto.stock_actual -= item.cantidad
                item.producto.save()
            
            # Actualizar total de venta
            venta.total = total
            venta.save()
            
            # Limpiar carrito
            items.delete()
            
            messages.success(request, f'¡Pedido #{venta.numero_venta} creado exitosamente!')
            return redirect('ventas:detalle_pedido', pk=venta.pk)
        
        except Exception as e:
            messages.error(request, f'Error al procesar el pedido: {str(e)}')
            return redirect('ventas:ver_carrito')
    
    context = {
        'carrito': carrito,
        'items': items,
        'total': carrito.total(),
    }
    return render(request, 'ventas/checkout.html', context)


@login_required
def historial_pedidos(request):
    """Muestra el historial de pedidos del cliente"""
    # Obtener ventas donde el usuario autenticado es el que las compró (cliente)
    from clientes.models import Cliente

    cliente = Cliente.objects.filter(email=request.user.email).first()
    
    if cliente:
        pedidos = Venta.objects.filter(cliente=cliente).prefetch_related('detalles')
    else:
        pedidos = Venta.objects.none()
    
    # Ordenar por fecha descendente
    pedidos = pedidos.order_by('-fecha')
    
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'ventas/historial_pedidos.html', context)


@login_required
def detalle_pedido(request, pk):
    """Muestra los detalles de un pedido"""
    pedido = get_object_or_404(Venta, pk=pk)
    
    # Permitir acceso al cliente dueño o al rol logístico/administrativo.
    if not user_has_role(request.user, 'admin', 'logistica') and pedido.cliente and pedido.cliente.email != request.user.email:
        messages.error(request, 'No tienes permiso para ver este pedido')
        return redirect('ventas:historial_pedidos')
    
    context = {
        'pedido': pedido,
        'detalles': pedido.detalles.all(),
    }
    template_name = 'ventas/detalle_pedido_logistica.html' if user_has_role(request.user, 'admin', 'logistica') else 'ventas/detalle_pedido.html'
    return render(request, template_name, context)
