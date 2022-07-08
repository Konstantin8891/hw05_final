import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser_forms')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='TestSlug',
            description='TestDescription',
        )
        cls.post = Post.objects.create(
            text='TestText',
            group=cls.group,
            author=cls.user,
        )
        cls.form = PostForm()
        cls.posts_count = Post.objects.count()
        cls.post_data_edit = {
            'text': 'EditedText',
            'group': cls.group.id,
            'author': cls.user
        }
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
        cls.post_data = {
            'text': 'CreatePost',
            'group': cls.group.id,
            'author': cls.user,
            'image': cls.uploaded
        }

    @classmethod
    def tearDownClass(cls):
        # удаление директории TEMP_MEDIA_ROOT
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.post_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text='CreatePost',
            group=self.group.id,
            author=self.user,
            image='posts/small.gif'
        ).exists())

    def test_post_edit(self):
        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=self.post_data_edit,
            follow=True
        )
        self.assertNotEqual(self.post_data_edit['text'], self.post.text)
