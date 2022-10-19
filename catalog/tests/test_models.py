from django.test import TestCase

import datetime

from catalog.models import Author
from catalog.models import Genre
from catalog.models import Book
from catalog.models import BookInstance
from catalog.models import Language
from catalog.models import User


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Настройка немодифицированных объектов, используемых всеми методами тестирования
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = '%s, %s' % (author.last_name, author.first_name)
        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # Не удастся, если urlconf не определен.
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')


class LanguageModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Настройка немодифицированных объектов, используемых всеми методами тестирования
        Language.objects.create(name='Mongolian')

    def test_language_name_label(self):
        language_name = Language.objects.get(id=1)
        field_label = language_name._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_language_name_max_length(self):
        language_name = Language.objects.get(id=1)
        max_length = language_name._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def test_object_language_comma_language(self):
        language = Language.objects.get(id=1)
        expected_object_name = '%s' % language.name
        self.assertEquals(expected_object_name, str(language))

    # urlconf не определен.


class GenreModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Настройка немодифицированных объектов, используемых всеми методами тестирования
        Genre.objects.create(name='Secret documentation')

    def test_name_label(self):
        name = Genre.objects.get(id=1)
        field_label = name._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_name_max_length(self):
        name = Genre.objects.get(id=1)
        max_length = name._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def test_object_name_is_genre_comma_genre(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = '%s' % genre.name
        self.assertEquals(expected_object_name, str(genre))


class BookModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Настройка немодифицированных объектов, используемых всеми методами тестирования
        Language.objects.create(name='Russian')
        Author.objects.create(first_name='Big', last_name='Bob')
        Genre.objects.create(name='Secret documentation')

        Book.objects.create(
            title='Big love',
            summary='Great book very well',
            isbn='123456789',
        )
        Book.author = Author.objects.get(id=1)
        Book.genre = Genre.objects.get(id=1)
        Book.language = Language.objects.get(id=1)

    def test_title_label(self):
        title = Book.objects.get(id=1)
        field_label = title._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_author_label(self):
        author = Book.objects.get(id=1)
        field_label = author._meta.get_field('author').verbose_name
        self.assertEquals(field_label, 'author')

    def test_summary_label(self):
        summary = Book.objects.get(id=1)
        field_label = summary._meta.get_field('summary').verbose_name
        self.assertEquals(field_label, 'summary')

    def test_isbn_label(self):
        isbn = Book.objects.get(id=1)
        field_label = isbn._meta.get_field('isbn').verbose_name
        self.assertEquals(field_label, 'ISBN')

    def test_genre_label(self):
        genre = Book.objects.get(id=1)
        field_label = genre._meta.get_field('genre').verbose_name
        self.assertEquals(field_label, 'genre')

    def test_language_label(self):
        language = Book.objects.get(id=1)
        field_label = language._meta.get_field('language').verbose_name
        self.assertEquals(field_label, 'language')

    def test_title_max_length(self):
        title = Book.objects.get(id=1)
        max_length = title._meta.get_field('title').max_length
        self.assertEquals(max_length, 200)

    def test_summary_max_length(self):
        summary = Book.objects.get(id=1)
        max_length = summary._meta.get_field('summary').max_length
        self.assertEquals(max_length, 1000)

    def test_isbn_max_length(self):
        isbn = Book.objects.get(id=1)
        max_length = isbn._meta.get_field('isbn').max_length
        self.assertEquals(max_length, 13)

    def test_object_book_title_comma_title(self):
        book = Book.objects.get(id=1)
        expected_object_name = '%s' % book.title
        self.assertEquals(expected_object_name, str(book))

    def test_object_book_author_comma_author(self):
        book = Book.objects.get(id=1)
        expected_object_name = '%s, %s' % (book.author.last_name, book.author.first_name)
        self.assertEquals(expected_object_name, str(book.author))

    def test_object_book_genre_comma_genre(self):
        book = Book.objects.get(id=1)
        expected_object_name = '%s' % book.genre.name
        self.assertEquals(expected_object_name, str(book.genre))

    def test_object_book_language_comma_language(self):
        book = Book.objects.get(id=1)
        expected_object_name = '%s' % book.language.name
        self.assertEquals(expected_object_name, str(book.language))

    def test_object_book_summary_comma_summary(self):
        book = Book.objects.get(id=1)
        expected_object_name = '%s' % book.summary
        self.assertEquals(expected_object_name, str(book.summary))

    def test_object_book_isbn_comma_isbn(self):
        book = Book.objects.get(id=1)
        expected_object_name = '%s' % book.isbn
        self.assertEquals(expected_object_name, str(book.isbn))

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        # Не удастся, если urlconf не определен.
        self.assertEquals(book.get_absolute_url(), '/catalog/book/1')


class BookInstanceModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Настройка немодифицированных объектов, используемых всеми методами тестирования
        User.objects.create_user("Anonimus")
        Language.objects.create(name='Russian')
        Author.objects.create(first_name='Big', last_name='Bob')
        Genre.objects.create(name='Secret documentation')

        Book.objects.create(
            title='Big love',
            summary='Great book very well',
            isbn='123456789',
        )
        Book.author = Author.objects.get(id=1)
        Book.genre = Genre.objects.get(id=1)
        Book.language = Language.objects.get(id=1)

        BookInstance.objects.create(imprint='Book in the list',
                                    due_back=datetime.date.fromisoformat('2019-12-04'),
                                    )
        BookInstance.book = Book.objects.get(id=1)
        BookInstance.borrower = User.objects.get(id=1)

    def test_imprint_label(self):
        imprint = BookInstance.objects.get()
        field_label = imprint._meta.get_field('imprint').verbose_name
        self.assertEquals(field_label, 'imprint')

    def test_due_back_label(self):
        due_back = BookInstance.objects.get()
        field_label = due_back._meta.get_field('due_back').verbose_name
        self.assertEquals(field_label, 'due back')

    def test_user_label(self):
        user = BookInstance.objects.get()
        field_label = user._meta.get_field('borrower').verbose_name
        self.assertEquals(field_label, 'borrower')

    def test_book_label(self):
        book = BookInstance.objects.get()
        field_label = book._meta.get_field('book').verbose_name
        self.assertEquals(field_label, 'book')

    def test_imprint_length(self):
        imprint = BookInstance.objects.get()
        max_length = imprint._meta.get_field('imprint').max_length
        self.assertEquals(max_length, 200)

    def test_object_book_inst_imprint_comma_imprint(self):
        book = BookInstance.objects.get()
        expected_object_name = '%s' % book.imprint
        self.assertEquals(expected_object_name, str(book.imprint))

    def test_object_book_inst_due_back_comma_due_back(self):
        book = BookInstance.objects.get()
        expected_object_name = '%s' % book.due_back
        self.assertEquals(expected_object_name, str(book.due_back))

    def test_object_book_inst_user_comma_user(self):
        book = BookInstance.objects.get()
        expected_object_name = '%s' % book.borrower
        self.assertEquals(expected_object_name, str(book.borrower))

    def test_object_book_inst_book_comma_book(self):
        book_inst = BookInstance.objects.get()
        expected_object_name = '%s' % book_inst.book.title
        self.assertEquals(expected_object_name, str(book_inst.book.title))

        #urlconf не определен.




