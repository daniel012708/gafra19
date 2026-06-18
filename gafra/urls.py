"""
URL configuration for gafra project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from usuario import views as usuario_views
from usuario.views_registro import registro_cliente_view
from django.urls import path, include
# agrega esta línea arriba con los imports:
import gafra.whatsapp_views as whatsapp_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')),
    path('productos/', include('productos.urls', namespace='productos')),
    path('proveedores/', include('proveedores.urls', namespace='proveedores')),
    path('produccion/', include('produccion.urls', namespace='produccion')),
    path('inventario/', include('inventario.urls', namespace='inventario')),
    path('ventas/', include('ventas.urls', namespace='ventas')),
    path('usuario/', include('usuario.urls', namespace='usuario')),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    # URLs de autenticación sin namespace para evitar conflicto
    path('login/', usuario_views.login_view, name='login'),
    path('logout/', usuario_views.logout_view, name='logout'),
    path('registro/', registro_cliente_view, name='registro_cliente'),
    path('whatsapp/', whatsapp_views.webhook, name='whatsapp_webhook'),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
