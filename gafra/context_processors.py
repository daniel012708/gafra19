from django.conf import settings
from .access import allowed_modules_for_user, current_module_from_request, get_user_role, get_user_role_label, sidebar_navigation_for_user

def static_version(request):
    """Provide a STATIC_VERSION for templates as a fallback when Manifest isn't used.

    When using CompressedManifestStaticFilesStorage this isn't necessary, but while
    developing this allows using ?v={{ STATIC_VERSION }} in templates when needed.
    """
    return { 'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1.0') }


def user_access(request):
    role = get_user_role(request.user)
    return {
        'current_user_role': role,
        'current_user_role_label': get_user_role_label(request.user),
        'allowed_modules': allowed_modules_for_user(request.user),
        'sidebar_navigation': sidebar_navigation_for_user(request.user),
        'current_module': current_module_from_request(request),
    }
