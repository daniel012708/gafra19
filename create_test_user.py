#!/usr/bin/env python
"""
Script para verificar y crear usuario cliente de prueba
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gafra.settings')
django.setup()

from django.contrib.auth.models import User
from usuario.models import Usuario

print("🔍 Verificando usuarios existentes...")

# Ver usuarios existentes
usuarios = User.objects.all()
if usuarios:
    print("\n👥 Usuarios existentes:")
    for user in usuarios:
        try:
            perfil = user.usuario_profile
            rol = perfil.rol
        except:
            rol = "Sin perfil"
        print(f"  - {user.username}: {user.email} - Rol: {rol}")
else:
    print("\n❌ No hay usuarios en la base de datos")

# Crear usuario cliente si no existe
cliente_username = "cliente_test"
cliente_email = "cliente@test.com"
cliente_password = "cliente123"

if not User.objects.filter(username=cliente_username).exists():
    print(f"\n👤 Creando usuario cliente: {cliente_username}")

    # Crear usuario de Django
    user = User.objects.create_user(
        username=cliente_username,
        email=cliente_email,
        password=cliente_password,
        first_name="Cliente",
        last_name="Prueba"
    )

    # Crear perfil de usuario con rol cliente
    Usuario.objects.create(
        user=user,
        rol='cliente'
    )

    print("✅ Usuario cliente creado exitosamente!")
    print(f"   Usuario: {cliente_username}")
    print(f"   Email: {cliente_email}")
    print(f"   Contraseña: {cliente_password}")
else:
    print(f"\n✅ El usuario cliente '{cliente_username}' ya existe")

print("\n🎉 ¡Listo!")