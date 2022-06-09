from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.page_list = [
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            )
        ]
        obj = [
            Post(
                author=cls.user,
                text='Тестовый пост Тестовый',
                group=cls.group
            )
            for i in range(13)
        ]
        cls.post = Post.objects.bulk_create(obj)

    def test_first_page_contains_ten_records(self):
        for url in self.page_list:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        for url in self.page_list:
            response = self.client.get(url + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
