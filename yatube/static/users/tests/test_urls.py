# posts/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            email='something@somewhere.com',
            password='testpassword',
            username='testuser'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client(enforce_csrf_checks=True)
        self.authorized_client.force_login(UsersURLTests.user)

    def test_guest_client_direct(self):
        urls = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
            '/auth/logout/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_client_redirect(self):
        url_redir = {
            '/auth/password_change/done/':
                '/auth/login/?next=/auth/password_change/done/',
            '/auth/password_change/':
                '/auth/login/?next=/auth/password_change/',
        }
        for address, redir in url_redir.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redir)

    def test_authorized_user(self):
        urls = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_templates(self):
        response = self.authorized_client.get('/auth/signup/')
        self.assertTemplateUsed(response, 'users/signup.html')
