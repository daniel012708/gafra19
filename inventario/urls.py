from django.urls import path
from . import views
from .views_entrada import EntradaMateriaPrimaView
from .views_historial import HistorialMateriaPrimaView
from .views_historial_general import HistorialGeneralMateriaPrimaView

app_name = 'inventario'

urlpatterns = [
    path('historial/', HistorialGeneralMateriaPrimaView.as_view(), name='historial_general'),
    path('', views.MateriaPrimaListView.as_view(), name='list'),
    path('<int:pk>/', views.MateriaPrimaDetailView.as_view(), name='detail'),
    path('nuevo/', views.MateriaPrimaCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.MateriaPrimaUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.MateriaPrimaDeleteView.as_view(), name='delete'),
    path('<int:pk>/entrada/', EntradaMateriaPrimaView.as_view(), name='entrada'),
    path('<int:pk>/historial/', HistorialMateriaPrimaView.as_view(), name='historial'),
    path('carga-masiva/', views.carga_masiva_materias, name='carga_masiva'),
]

# Reportes: simple view rendered inline
from django.shortcuts import render
from django.db.models import F
from .models import MateriaPrima

urlpatterns += [
    path('reportes/', views.reportes, name='reportes'),
]