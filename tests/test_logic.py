from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotesCreation(TestCase):
    COUNT_NOTE_NONE = 0
    COUNT_NOTE_ONE = 1
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Читатель')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text=cls.NOTE_TEXT,
            slug='Heading',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'Heading',
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_anonymous_user_cant_create_note(self):
        initial_number_of_notes = Note.objects.count()
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), initial_number_of_notes)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        self.author_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(self.form_data['title'], note.title)
        self.assertEqual(self.form_data['text'], note.text)
        self.assertEqual(self.form_data['slug'], note.slug)
        self.assertEqual(self.author, note.author)

    def test_user_cannot_create_note_with_duplicate_slug(self):
        count_beginning_test = Note.objects.count()
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )
        self.assertEqual(Note.objects.count(), count_beginning_test)

    def test_author_can_delete_note(self):
        initial_number_of_notes = Note.objects.count() - 1
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, '/done/')
        self.assertEqual(Note.objects.count(), initial_number_of_notes)

    def test_user_cant_delete_note_of_another_author(self):
        initial_number_of_notes = Note.objects.count()
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), initial_number_of_notes)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_author(self):
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
