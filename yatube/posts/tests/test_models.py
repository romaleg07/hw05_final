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
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Тестовый пост Тестовый пост'
        )

    def test_models_have_correct_object_names(self):
        task_group = PostModelTest.group
        task_post = PostModelTest.post

        self.assertEquals(task_group.__str__(), 'Тестовая группа')
        self.assertEquals(
            task_post.__str__(),
            'Тестовый пост Тестовый пост Тестовый пост'[:15]
        )

    def test_models_correct_verbose_name(self):
        task_post = PostModelTest.post
        verbose_fields = {
            'text': 'Запись',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in verbose_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task_post._meta.get_field(value).verbose_name, expected)

    def test_models_correct_help_text(self):
        task_post = PostModelTest.post
        help_text_fields = {
            'text': 'Введите текст записи',
            'group': 'Выберите группу',
        }
        for value, expected in help_text_fields.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task_post._meta.get_field(value).help_text, expected)
