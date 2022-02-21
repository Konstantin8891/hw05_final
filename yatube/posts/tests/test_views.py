import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from time import sleep

from ..models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser_views')
        cls.subscriber = User.objects.create_user(username='test_subscriber')
        cls.another_subscriber = User.objects.create_user(
            username='test_anothersubscriber'
        )
        cls.group = Group.objects.create(
            title='testgroup',
            slug='testslug',
            description='testdescription',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='testpost',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )
        cls.page_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.pk}
            ): 'posts/create_post.html',
        }
        cls.reverses_editable = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': cls.post.pk}),
        ]
        cls.reverses_read_only_create = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username}),
        ]
        cls.another_group = Group.objects.create(
            title='another_group',
            slug='anotherslug',
            description='anotherdescription',
        )
        cls.post_data = {
            'text': 'TestCreatePost',
            'group': cls.group.id,
        }
        cls.comment_data = {
            'post': cls.post,
            'author': cls.user,
            'text': 'TestComment',
        }
        cls.post_subscribe_data = {
            'author': cls.user,
            'text': 'SubscribePost',
            'group': cls.group.id,
        }

    @classmethod
    def tearDownClass(cls):
        # удаление директории TEMP_MEDIA_ROOT
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        cache.clear()

    def test_pages_names(self):
        cache.clear()
        for page, template in self.page_template.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_editable_context(self):
        for rev in self.reverses_editable:
            with self.subTest(rev=rev):
                response = self.authorized_client.get(rev)
                self.assertIn('form', response.context)

    # тест контекста index, group_list_profile
    def test_correct_read_only_context(self):
        cache.clear()
        for rev in self.reverses_read_only_create:
            with self.subTest(rev=rev):
                response = self.authorized_client.get(rev)
                first_object = response.context['page_obj'][0]
                post_text = first_object.text
                post_group = first_object.group
                post_author = first_object.author
                post_image = first_object.image
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_group, self.post.group)
                self.assertEqual(post_author, self.post.author)
                self.assertEqual(post_image, self.post.image)

    # Тест контекста post_detail
    def test_post_detail_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        post_obj = response.context['post']
        post_text = post_obj.text
        post_group = post_obj.group
        post_author = post_obj.author
        post_image = post_obj.image
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_image, self.post.image)

    # Тест создания поста
    def test_post_create(self):
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.post_data,
            follow=True,
        )
        cache.clear()
        for rev in self.reverses_read_only_create:
            with self.subTest(rev=rev):
                response = self.authorized_client.get(rev)
                first_object = response.context['page_obj'][0]
                post_text = first_object.text
                post_group = first_object.group.id
                post_author = first_object.author
                self.assertEqual(post_text, self.post_data['text'])
                if rev == reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                ):
                    self.assertFalse(Post.objects.filter(
                        text='TestText',
                        group=self.another_group.id,
                        author=self.user).exists()
                    )
                self.assertEqual(post_group, self.post_data['group'])
                self.assertEqual(post_author, self.post.author)

    # Тест добавления коммента неавторизованным юзером
    def test_guest_comment_create(self):
        self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data=self.comment_data,
            follow=True,
        )
        self.assertFalse(Comment.objects.filter(
            text=self.comment_data['text']
        ).exists())

    # Тест добавления коммента авторизованным юзером
    def test_authorized_comment_create(self):
        self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data=self.comment_data,
            follow=True,
        )
        self.assertTrue(Comment.objects.filter(
            text=self.comment_data['text']
        ).exists())

    def test_authorized_subscribe_unsubscribe(self):
        self.authorized_client.force_login(self.subscriber)
        subscribe = Follow.objects.create(
            user=self.subscriber,
            author=self.user
        )
        self.assertTrue(Follow.objects.filter(
            user=self.subscriber,
            author=self.user
        ).exists())
        subscribe.delete()
        self.assertFalse(Follow.objects.filter(
            user=self.subscriber,
            author=self.user
        ).exists())

    def test_post_subscribe(self):
        self.authorized_client.force_login(self.user)
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.post_subscribe_data,
            follow=True,
        )
        self.authorized_client.force_login(self.subscriber)
        Follow.objects.create(user=self.subscriber, author=self.user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context["page_obj"][0].text,
            self.post_subscribe_data['text']
        )
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.subscriber
        ).exists())


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser_paginator')
        cls.group = Group.objects.create(
            title='testgroup',
            slug='testslug_paginator',
            description='testdescription',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text=f'testpost{i}',
                group=cls.group,
                author=cls.user,
            )
        cls.reverses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username})
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        

    def test_first_page_contains_ten_records(self):
        cache.clear()
        for rev in PaginatorViewsTest.reverses:
            with self.subTest(rev=rev):
                response = self.client.get(rev)
                # Проверка: количество постов на первой странице равно 10.
                self.assertEqual(
                    response.
                    context['page_obj'].
                    paginator.page(1).
                    object_list.count(),
                    10
                )

    def test_second_page_contains_three_records(self):
        for rev in PaginatorViewsTest.reverses:
            with self.subTest(rev=rev):
                # Проверка: на второй странице должно быть три поста.
                cache.clear()
                response = self.client.get(reverse('posts:index') + '?page=2')
                self.assertEqual(
                    response.
                    context['page_obj'].
                    paginator.page(2).
                    object_list.count(),
                    3
                )


class CacheTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser_cache')
        cls.group = Group.objects.create(
            title='testtitle',
            slug='testslug',
            description='testdescription',
        )
        cls.post = Post.objects.create(
            text='cachetext',
            author=cls.user
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_index_cache(self):
        response = self.authorized_client.get(reverse('posts:index'))
        context = response.context['page_obj']
        content = response.content
        self.assertIn(self.post, context)
        post = Post.objects.filter(pk=self.post.id)
        post.delete()
        response_refresh = self.authorized_client.get(reverse('posts:index'))
        content_refresh = response_refresh.content
        self.assertEqual(content, content_refresh)
        cache.clear()
        new_response_refresh = self.authorized_client.get(reverse(
            'posts:index'
        ))
        new_content_refresh = new_response_refresh.content
        self.assertNotEqual(content, new_content_refresh)
