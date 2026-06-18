from django.urls import path
from . import views
from usuario import views as usuario_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('become-admin/', usuario_views.become_admin, name='become_admin'),
]
