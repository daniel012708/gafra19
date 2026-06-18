from functools import wraps

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

SIDEBAR_ITEMS = [
    {
        'key': 'dashboard',
        'label': 'Inicio',
        'icon': 'bi-house-door',
        'url_name': 'dashboard:index',
    },
    {
        'key': 'usuario',
        'label': 'Usuarios',
        'icon': 'bi-people',
        'url_name': 'usuario:list',
    },
    {
        'key': 'proveedores',
        'label': 'Proveedores',
        'icon': 'bi-truck',
        'url_name': 'proveedores:list',
    },
    {
        'key': 'inventario',
        'label': 'Inventario',
        'icon': 'bi-box-seam',
        'url_name': 'inventario:list',
    },
    {
        'key': 'productos',
        'label': 'Productos',
        'icon': 'bi-basket',
        'url_name': 'productos:list',
    },
    {
        'key': 'produccion',
        'label': 'Producción',
        'icon': 'bi-gear',
        'url_name': 'produccion:list',
    },
    {
        'key': 'clientes',
        'label': 'Clientes',
        'icon': 'bi-person-lines-fill',
        'url_name': 'clientes:list',
    },
    {
        'key': 'ventas',
        'label': 'Ventas',
        'icon': 'bi-receipt',
        'url_name': 'ventas:lista',
        'logistica_url_name': 'ventas:pedidos_logistica',
        'logistica_label': 'Pedidos',
    },
]


ROLE_MODULES = {
    'admin': {'usuario', 'proveedores', 'inventario', 'productos', 'produccion', 'clientes', 'ventas'},
    'vendedor': {'clientes', 'productos', 'ventas'},
    'almacenista': {'proveedores', 'inventario', 'productos'},
    'logistica': {'inventario', 'productos', 'produccion', 'ventas'},
    'cliente': {'productos', 'ventas'},
}


ROLE_LABELS = {
    'admin': 'Administrador',
    'vendedor': 'Vendedor',
    'almacenista': 'Almacenista',
    'logistica': 'Logística',
    'cliente': 'Cliente',
}


def get_user_role(user):
    if not getattr(user, 'is_authenticated', False):
        return 'anonymous'

    usuario = getattr(user, 'usuario', None)
    if usuario is None:
        try:
            usuario = user.usuario
        except Exception:
            usuario = None

    if usuario and getattr(usuario, 'rol', None):
        return usuario.rol
    if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
        return 'admin'
    return 'cliente'


def get_user_role_label(user):
    return ROLE_LABELS.get(get_user_role(user), 'Usuario')


def user_has_role(user, *roles):
    role = get_user_role(user)
    if role == 'admin':
        return True
    return role in roles


def allowed_modules_for_user(user):
    role = get_user_role(user)
    if role == 'admin':
        return {'dashboard', 'usuario', 'proveedores', 'inventario', 'productos', 'produccion', 'clientes', 'ventas'}
    return ROLE_MODULES.get(role, set())


def sidebar_navigation_for_user(user):
    allowed_modules = allowed_modules_for_user(user)
    role = get_user_role(user)
    navigation = []

    for item in SIDEBAR_ITEMS:
        if item['key'] != 'dashboard' and item['key'] not in allowed_modules:
            continue

        entry = dict(item)
        if item['key'] == 'ventas' and role == 'logistica':
            entry['url_name'] = item['logistica_url_name']
            entry['label'] = item['logistica_label']
        navigation.append(entry)

    return navigation


def current_module_from_request(request):
    match = getattr(request, 'resolver_match', None)
    if match and match.namespace:
        return match.namespace

    path = (getattr(request, 'path', '') or '').strip('/')
    if not path:
        return 'dashboard'
    return path.split('/')[0]


class ModuleAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    module_key = None
    allowed_roles = ()
    permission_denied_message = 'No tienes permisos para acceder a esta sección.'

    def test_func(self):
        user = self.request.user
        if not getattr(user, 'is_authenticated', False):
            return False
        if self.module_key and self.module_key not in allowed_modules_for_user(user):
            return False
        if self.allowed_roles and not user_has_role(user, *self.allowed_roles):
            return False
        return True

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect('dashboard:index')
        return super().handle_no_permission()


def module_access_required(*roles, module_key=None, message='No tienes permisos para acceder a esta sección.'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not getattr(user, 'is_authenticated', False):
                return redirect('login')
            if module_key and module_key not in allowed_modules_for_user(user):
                messages.error(request, message)
                return redirect('dashboard:index')
            if roles and not user_has_role(user, *roles):
                messages.error(request, message)
                return redirect('dashboard:index')
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator