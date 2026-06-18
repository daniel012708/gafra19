#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create admin user if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@gafra.com', 'admin123')
    print('Admin user created successfully!')
    print('Username: admin')
    print('Password: admin123')
else:
    print('Admin user already exists')

# Create a regular client user
if not User.objects.filter(username='cliente').exists():
    client_user = User.objects.create_user('cliente', 'cliente@gafra.com', 'cliente123')
    client_user.first_name = 'Juan'
    client_user.last_name = 'Pérez'
    client_user.save()
    print('Client user created successfully!')
    print('Username: cliente')
    print('Password: cliente123')
else:
    print('Client user already exists')