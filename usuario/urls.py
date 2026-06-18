from django.urls import path
from . import views
from .views_registro import registro_cliente_view

app_name = 'usuario'

urlpatterns = [
    path('reportes/', views.reportes, name='reportes'),
    path('carga-masiva/', views.carga_masiva_usuarios, name='carga_masiva'),
    path('', views.UsuarioListView.as_view(), name='list'),
    path('nuevo/', views.UsuarioCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='delete'),
    path('profile/', views.profile_view, name='profile'),
    path('registro/', registro_cliente_view, name='registro_cliente'),
]