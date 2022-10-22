from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, Follow
from users.models import User


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание2',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.upload = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Тестовый',
            group=cls.group,
            image=cls.upload
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.new_author = User.objects.create_user(username='new_author')

    def test_pages_uses_correct_template(self):
        list_urls = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', args=['test_slug']
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=[self.user.username]
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
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def check_correct_page_object(self, page_object):
        first_object = page_object[0]
        self.assertEqual(first_object.text, 'Тестовый пост Тестовый')
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_index_page_show_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        page_object = response.context['page_obj']
        self.check_correct_page_object(page_object)

    def test_groups_posts_page_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}
        ))
        page_object = response.context['page_obj']
        self.check_correct_page_object(page_object)
        self.assertEqual(response.context['group'].title, 'Тестовая группа')

    def test_profile_page_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}
        ))
        page_object = response.context['page_obj']
        self.check_correct_page_object(page_object)
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(
            response.context['count'],
            Post.objects.filter(author=self.user).count()
        )

    def test_group_page_dont_show_another_group_posts(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug2'}
        ))
        self.assertFalse(response.context['page_obj'])

    def test_post_detail_page_show_correct_content(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        post = response.context['post']
        count_author_posts = response.context['count']
        self.assertEqual(post.text, 'Тестовый пост Тестовый')
        self.assertEqual(post.author.username, 'auth')
        self.assertEqual(post.group.title, 'Тестовая группа')
        self.assertEqual(post.group.slug, 'test_slug')
        self.assertEqual(count_author_posts, 1)

    def test_post_edit_page_show_correct_content(self):
        pages_list = [
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ),
            reverse(
                'posts:post_create'
            ),
        ]
        for url in pages_list:
            response = self.authorized_client.get(url)
            form_fields = {
                'group': forms.models.ModelChoiceField,
                'text': forms.fields.CharField,
            }
            for value, expected in form_fields.items():
                with self.subTest(expected=expected):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_detail_page_comment_for_guest_user(self):
        form_data = {
            'text': 'text'
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/comment/')

    def test_post_detail_page_add_new_comment(self):
        form_data = {
            'author': self.user,
            'text': 'Тестовый комментарий',
            'post': self.post
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
        )
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, 'Тестовый комментарий')

    def test_cahce_index_page(self):
        response = self.authorized_client.get(reverse('posts:index'))
        old_posts = response.content
        Post.objects.create(
            author=self.user,
            text='Проверка кеша',
        )
        # check create new post
        self.assertTrue(Post.objects.filter(
            text='Проверка кеша'
        ).exists())
        # check cache
        response = self.authorized_client.get(reverse('posts:index'))
        new_posts = response.content
        self.assertEqual(new_posts, old_posts)

    def test_correct_following_authors(self):
        # проверяем добавление подписки и вывод постов
        Post.objects.create(
            author=self.new_author,
            text='Новый пост',
        )
        Follow.objects.create(
            user=self.user,
            author=self.new_author
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        first_post = page_object[0]
        self.assertEqual(first_post.text, 'Новый пост')
        # проверяем корректное удаление подписки
        Follow.objects.get(
            user=self.user,
            author=self.new_author
        ).delete()
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        self.assertFalse(page_object)

    def test_correct_content_following_users(self):
        # первого создал в setup-классе, не знаю как правильней
        new_author_2 = User.objects.create_user(username='new_author_2')
        new_user = User.objects.create_user(username='new_user')
        new_user_client = Client()
        new_user_client.force_login(new_user)
        Post.objects.create(
            author=self.new_author,
            text='Новый пост',
        )
        Post.objects.create(
            author=new_author_2,
            text='Новый Пост2'
        )
        obj = [
            Follow(
                user=self.user,
                author=self.new_author
            ),
            Follow(
                user=self.user,
                author=new_author_2
            ),
            Follow(
                user=new_user,
                author=self.new_author
            )
        ]
        Follow.objects.bulk_create(obj)
        response_first = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        count_for_first_user = len(
            response_first.context['page_obj']
        )
        response_second = new_user_client.get(
            reverse('posts:follow_index')
        )
        count_for_second_user = len(
            response_second.context['page_obj']
        )
        self.assertNotEqual(count_for_first_user, count_for_second_user)
