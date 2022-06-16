from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
            'image': 'Картинка'
        }
        cls.field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу'
        }

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(
            self.group.title,
            str(self.group),
            'метод __str__ модели Post работает некорректно'
        )
        post = self.post
        expected = post.text[:15]
        self.assertEqual(expected, str(post))

    def test_max_length_group_title(self):
        max_length_title = self.group._meta.get_field('title').max_length
        length_title = len(self.group.title)
        self.assertTrue(
            max_length_title >= length_title,
            'превышение максимальной длины поля title модели group'
        )

    def test_verbose_name_post(self):
        for value, expected in self.field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_help_text_group(self):
        for value, expected in self.field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text,
                    expected
                )
