import os
import django
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH so 'gafra' settings module is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from django.test import Client

User = get_user_model()

tests = [('admin', '123'), ('cliente', '123')]

for u, p in tests:
    # direct DB check
    try:
        dbu = User.objects.get(username=u)
        print(f"User '{u}' in DB, password hash startswith: {dbu.password[:10]}...")
        print('  check_password(123)=', dbu.check_password(p))
    except Exception as e:
        print('  user lookup error:', e)

    user = authenticate(username=u, password=p)
    print(f"User '{u}' authenticate: {bool(user)}")
    if user:
        print('  is_staff=', user.is_staff, 'is_superuser=', user.is_superuser)

    # allow testserver host for test client requests
    from django.conf import settings
    try:
        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']
    except Exception:
        pass

    c = Client()
    ok = c.login(username=u, password=p)
    print('  client.login ->', ok)
    r_admin = c.get('/admin/', HTTP_HOST='127.0.0.1')
    print('  GET /admin/ =>', r_admin.status_code)
    r_prod = c.get('/productos/', HTTP_HOST='127.0.0.1')
    print('  GET /productos/ =>', r_prod.status_code)
