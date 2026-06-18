from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('reportes/', views.reportes, name='reportes'),
    path('carga-masiva/', views.carga_masiva_clientes, name='carga_masiva'),
    path('', views.ClienteListView.as_view(), name='list'),
    path('nuevo/', views.ClienteCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='delete'),
]
