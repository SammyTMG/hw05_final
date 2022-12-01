import shutil
import tempfile

from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Post, Group, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NameSurname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.user2 = User.objects.create_user(username='NameSurname2')
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            description='Тестовое описание 1',
            slug='test_slug1'
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
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewesTests.user)
        self.username = PostViewesTests.user.username

    def test_views_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        post_text_0 = first_post.text
        post_author_0 = first_post.author.username
        post_group_0 = first_post.group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.username)
        self.assertEqual(post_group_0, self.group.title)

    def test_group_list__correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_post = response.context['page_obj'][0]
        post_group_text_0 = first_post.text
        post_group_author_0 = first_post.author.username
        post_group_0 = first_post.group.title
        post_slug_0 = first_post.group.slug
        post_group_description_0 = first_post.group.description
        self.assertEqual(post_group_text_0, self.post.text)
        self.assertEqual(post_group_author_0, self.username)
        self.assertEqual(post_group_0, self.group.title)
        self.assertEqual(post_slug_0, self.group.slug)
        self.assertEqual(post_group_description_0, self.group.description)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.post.author})
        )
        first_post = response.context['page_obj'][0]
        post_text_0 = first_post.text
        post_author_0 = first_post.author.username
        post_group_0 = first_post.group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.username)
        self.assertEqual(post_group_0, self.group.title)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id},
            )
        )
        post = Post.objects.filter(id=self.post.id)[0]
        objects = response.context['post']
        self.assertEqual(objects, post)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        post = Post.objects.filter(id=self.post.id)[0]
        objects = response.context['post']
        self.assertEqual(objects, post)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_group_and_not_in_other_group(self):
        """
        Проверяем, пост с группой на страницах и не попал в другую группу.
        """
        post_in_links = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group1.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ),
        ]

        new_post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group1,
        )
        for reverse_link in post_in_links:
            with self.subTest(reverse_link=reverse_link):
                response = self.authorized_client.get(reverse_link)
                self.assertIn(new_post, response.context['page_obj'])

        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertNotIn(new_post, response.context['page_obj'])

    def test_image_in_index_group_list_profile(self):
        """
        Проверяем, что картинка отображается на страницах
        """
        templates = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.post.author}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        )
        for url in templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                posts = response.context['page_obj'][0]
                self.assertEqual(posts.image, self.post.image)

    def test_image_in_post_detail(self):
        """Проверяем, что картинка отображается в post_detail"""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        posts = response.context['post']
        self.assertEqual(posts.image, self.post.image)

    def test_image_in_page(self):
        """Проверяем. что пост с картинкой создается в БД"""
        self.assertTrue(
            Post.objects.filter(text="Тестовый текст",
                                image="posts/small.gif").exists()
        )

    def test_comment_correct_context(self):
        """Валидная форма комментария создает запись в Post"""
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент', }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Тестовый коммент'
        ).exists())

    def test_cache(self):
        """Проверка кэша на странице index"""
        response = self.authorized_client.get(reverse('posts:index'))
        resp_1 = response.content
        Post.objects.get(id=1).delete()
        response2 = self.authorized_client.get(reverse('posts:index'))
        resp_2 = response2.content
        self.assertEqual(resp_1, resp_2)

    def test_follow(self):
        """ Авторизованный пользователь может подписаться"""
        follow_1 = self.user.follower.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.user2.username])
        )
        follow_2 = self.user.follower.count()
        self.assertEqual(follow_1 + 1, follow_2)

    def test_unfollow(self):
        """ Авторизованный пользователь может отписаться"""
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.user2.username])
        )
        follow_1 = self.user.follower.count()
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=[self.user2.username])
        )
        follow_2 = self.user.follower.count()
        self.assertEqual(follow_1, follow_2 + 1)

    def test_follow_new_post(self):
        """Пост появляется у тех, кто подписан и
        не появляется у тех, кто не подписан."""
        Follow.objects.get_or_create(user=self.user, author=self.post.author)
        follow = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, follow.context['page_obj'])

        nofollow = User.objects.create(username='NoFollow')
        self.authorized_client.force_login(nofollow)
        follow_2 = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, follow_2.context['page_obj'])


ALL_POSTS = 13
POSTS_P_ONE = 10
POSTS_P_TWO = 3


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for i in range(ALL_POSTS):
            cls.post = Post.objects.create(
                text=f'Тест поста {i}',
                author=cls.user,
            )

    def test_first_page_contains_ten_records(self):
        """На первой странице index первые 10 постов"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), POSTS_P_ONE)

    def test_second_page_contains_three_records(self):
        """На второй странице index другие 3 поста"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), POSTS_P_TWO)
