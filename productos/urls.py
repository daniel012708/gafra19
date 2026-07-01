from django.urls import path
from . import views
from .views_historial_general import HistorialGeneralProductoView
from .views_movimiento import ProductoMovimientoCreateView
from .views_historial import HistorialProductoView

app_name = 'productos'

urlpatterns = [
    path('historial/', HistorialGeneralProductoView.as_view(), name='historial_general'),
    path('movimiento/nuevo/', ProductoMovimientoCreateView.as_view(), name='movimiento_add'),
    path('reportes/', views.reportes, name='reportes'),
    path('carga-masiva/', views.carga_masiva_productos, name='carga_masiva'),
    path('', views.ProductoListView.as_view(), name='list'),
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='detail'),
    path('nuevo/', views.ProductoCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ProductoToggleActivoView.as_view(), name='delete'),
    path('<int:pk>/historial/', HistorialProductoView.as_view(), name='historial'),
]