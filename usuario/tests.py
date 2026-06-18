from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Usuario


class UsuarioViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.u = Usuario.objects.create(user=self.user, rol='vendedor', telefono='123', activo=True)

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
        other = User.objects.create_user(username='other', password='pass')
        data = {'user': other.id, 'rol': 'almacenista', 'telefono': '000', 'activo': True}
        response = self.client.post(reverse('usuario:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Usuario.objects.filter(user__username='other').exists())

