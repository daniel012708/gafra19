from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Usuario


class UsuarioViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.u = Usuario.objects.create(user=self.user, rol='admin', telefono='123', activo=True)

    def test_list_requires_login(self):
        response = self.client.get(reverse('usuario:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_items(self):
        self.client.login(username='tester', password='pass')
        response = self.client.get(reverse('usuario:list'))
        self.assertContains(response, 'tester')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.client.login(username='tester', password='pass')
        data = {
            'username': 'otheruser',
            'first_name': 'Ana',
            'last_name': 'Ruiz',
            'email': 'otheruser@example.com',
            'password': 'StrongPass1!',
            'password_confirm': 'StrongPass1!',
            'rol': 'almacenista',
            'telefono': '3001234567',
            'activo': 'on',
        }
        response = self.client.post(reverse('usuario:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(user__username='otheruser').exists())

