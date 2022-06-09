from django.test import TestCase
from ..models import Post, Group
from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostFormsTest(TestCase):
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
            text='Тестовый пост Тестовый',
            group=cls.group
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание2',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_form_post(self):
        posts_count = Post.objects.count()
        posts_count_in_group = Post.objects.filter(
            group=self.group
        ).count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        upload = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовая запись из теста',
            'author': self.user,
            'group': self.group.pk,
            'image': upload
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            Post.objects.filter(group=self.group).count(),
            posts_count_in_group + 1, self.group
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовая запись из теста',
                author=self.user,
                group=self.group
            ).exists()
        )

    def test_edit_form_post(self):
        post_text = Post.objects.filter(pk=self.post.pk)
        form_data = {
            'text': 'Новый тестовый пост',
            'group': self.group2.pk
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertNotEqual(
            post_text,
            Post.objects.filter(pk=self.post.pk)
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый пост',
                author=self.user,
                group=self.group2
            ).exists()
        )
