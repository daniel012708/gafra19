from django.urls import path
from . import views

app_name = 'produccion'

urlpatterns = [
    path('reportes/', views.reportes, name='reportes'),
    path('carga-masiva/', views.carga_masiva_ordenes, name='carga_masiva'),
    path('', views.OrdenProduccionListView.as_view(), name='list'),
    path('<int:pk>/', views.OrdenProduccionDetailView.as_view(), name='detail'),
    path('nuevo/', views.OrdenProduccionCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.OrdenProduccionUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.OrdenProduccionDeleteView.as_view(), name='delete'),
    path('<int:pk>/iniciar/', views.orden_produccion_iniciar, name='iniciar'),
    path('<int:pk>/completar/', views.orden_produccion_completar, name='completar'),
]
