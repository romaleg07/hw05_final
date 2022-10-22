from django.test import TestCase, Client
from django.urls import reverse
from ..models import Group, Post
from http import HTTPStatus
from users.models import User


class PostsUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост Тестовый пост Тестовый пост'
        )

    def setUp(self):
        self.guest_user = Client()
        self.user = User.objects.create_user(username='JustUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_url_correct_names(self):
        list_reverse_urls = {
            reverse(
                'posts:index'
            ): '/',
            reverse(
                'posts:group_list', args=['test_slug']
            ): '/group/test_slug/',
            reverse(
                'posts:profile', args=[self.author.username]
            ): '/profile/author/',
            reverse(
                'posts:post_detail', args=[self.post.pk]
            ): '/posts/' + str(self.post.pk) + '/',
            reverse(
                'posts:post_edit', args=[self.post.pk]
            ): '/posts/' + str(self.post.pk) + '/edit/',
            reverse(
                'posts:post_create'
            ): '/create/',
        }

        for reversed_name, url in list_reverse_urls.items():
            with self.subTest(url=url):
                self.assertEqual(url, reversed_name)

    def test_url_correct_templates(self):
        list_urls = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', args=['test_slug']
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=[self.author.username]
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=[self.post.pk]
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', args=[self.post.pk]
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }

        for url, template in list_urls.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_pages_for_all_users(self):
        list_urls_for_all_users = [
            reverse('posts:index'),
            reverse('posts:group_list', args=['test_slug']),
            reverse('posts:profile', args=[self.author.username]),
            reverse('posts:post_detail', args=[self.post.pk]),
        ]
        for url in list_urls_for_all_users:
            response = self.guest_user.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_page(self):
        response = self.guest_user.get('/group/idkwhat404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_post_create_for_guest(self):
        response = self.guest_user.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_redirect_post_edit_for_authorized_user(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', args=[self.post.pk]
            ),
            follow=True)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', args=[self.post.pk]
            ))
