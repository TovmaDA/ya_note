from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestListPage(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.user = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Просто текст.',
            slug='Heading',
            author=cls.author,
        )

    def test_notes_count_author_and_user(self):
        users_notes_counts = (
            (self.author, True,),
            (self.user, False,),
        )
        for user, count in users_notes_counts:
            with self.subTest(user=user, count=count):
                self.client.force_login(user)
                response = self.client.get(self.LIST_URL)
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                notes = Note.objects.get()
                self.assertIs(notes in object_list, count)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for name, args in (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        ):
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
