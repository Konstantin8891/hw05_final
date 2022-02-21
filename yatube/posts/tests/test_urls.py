# posts/tests/test_urls.py
from http import HTTPStatus

from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.empty_user = User.objects.create_user(username='empty_user')
        cls.group = Group.objects.create(
            title='тестовая группа',
            slug='testslug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='тестовый текст',
            group=cls.group,
            author=cls.user
        )
        cls.url_status = {
            '/unexisting_page': HTTPStatus.NOT_FOUND,
            '/': HTTPStatus.OK,
            '/profile/testuser/': HTTPStatus.OK,
            f'/posts/{cls.post.pk}': HTTPStatus.OK,
            f'/group/{cls.group.slug}/': HTTPStatus.OK,
        }
        cls.url_redirect = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{cls.post.pk}/edit': '/posts/1',
        }
        cls.urls = [
            '/create/',
            f'/posts/{cls.post.pk}/edit',
        ]
        cls.url_template = {
            '/': 'posts/index.html',
            f'/profile/{cls.user}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}': 'posts/post_detail.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit': 'posts/create_post.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client = Client()

    def test_guest_client_direct(self):
        for address, status in self.url_status.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_guest_client_redirect(self):
        for address, redir_address in self.url_redirect.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redir_address)

    def test_authorized_user(self):
        for url in self.urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_another_authorized(self):
        self.another_authorized_client.force_login(self.empty_user)
        response = self.another_authorized_client.get('/posts/1/edit')
        # Утверждаем, что для прохождения теста код должен быть равен 302
        self.assertRedirects(response, '/posts/1')

    def test_templates(self):
        cache.clear()
        for url, template in self.url_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
