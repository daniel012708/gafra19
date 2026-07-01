from django.urls import path
from . import views
from .views_historial import ProveedorHistorialView
from .views_historial_general import ProveedorHistorialGeneralView

app_name = 'proveedores'

urlpatterns = [
    path('', views.ProveedorListView.as_view(), name='list'),
    path('<int:pk>/', views.ProveedorDetailView.as_view(), name='detail'),
    path('nuevo/', views.ProveedorCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ProveedorToggleActivoView.as_view(), name='delete'),
    path('<int:pk>/historial/', ProveedorHistorialView.as_view(), name='historial'),
    path('historial-general/', ProveedorHistorialGeneralView.as_view(), name='historial_general'),
    path('carga-masiva/', views.carga_masiva_proveedores, name='carga_masiva'),
    ]
    
urlpatterns += [
    path('reportes/', views.reportes, name='reportes'),
]