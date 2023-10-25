from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='Heading',
            author=cls.author,
        )

    def test_pages_availability(self):
        urls = ('notes:home', 'users:login', 'users:logout', 'users:signup',)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                """ Без переменной не работает """
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_notes_list_edit_and_delete(self):
        users_statuses_urls = (
            (
                self.author,
                HTTPStatus.OK,
                (
                    ('notes:list', None),
                    ('notes:success', None),
                    ('notes:add', None),
                )
            ),
            (
                self.user,
                HTTPStatus.NOT_FOUND,
                (
                    ('notes:detail', (self.note.slug,)),
                    ('notes:delete', (self.note.slug,)),
                    ('notes:edit', (self.note.slug,))
                ),
            ),
        )
        for user, status, urls in users_statuses_urls:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    """ Без переменной не работает """
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
