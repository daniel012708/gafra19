from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('reportes/', views.reportes, name='reportes'),
   path('reportes/pdf/', views.reportes, name='reportes_pdf'),
    path('carga-masiva/', views.carga_masiva_ventas, name='carga_masiva'),
   path('logistica/pedidos/', views.logistica_pedidos, name='pedidos_logistica'),
   path('logistica/pedidos/<int:pk>/completar/', views.completar_pedido_logistica, name='completar_pedido_logistica'),
       path('', views.VentaListView.as_view(), name='lista'),
       path('<int:pk>/', views.VentaDetailView.as_view(), name='detalle'),
    path('nueva/', views.nueva_venta, name='crear'),
      path('confirmar/', views.confirmar_venta, name='confirmar'),
       path('<int:pk>/editar/', views.VentaUpdateView.as_view(), name='editar'),
       path('<int:pk>/eliminar/', views.VentaDeleteView.as_view(), name='eliminar'),
    
    # URLs para clientes
    path('catalogo/', views.catalogo_cliente, name='catalogo_cliente'),
    path('pre_catalogo/', views.catalogo_publico, name='catalogo_publico'),
    path('reportes/', views.reportes, name='reportes'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('actualizar-carrito/<int:item_id>/', views.actualizar_cantidad_carrito, name='actualizar_carrito'),
    path('eliminar-carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_carrito'),
    path('favoritos/agregar/<int:producto_id>/', views.agregar_favorito, name='agregar_favorito'),
    path('favoritos/', views.ver_favoritos, name='ver_favoritos'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('pedidos/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
]