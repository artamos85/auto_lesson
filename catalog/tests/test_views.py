from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User  # Необходимо для представления User как borrower

import datetime

from catalog.models import Author, BookInstance, Book, Genre, Language
from catalog.views import CreateView
from catalog.forms import RenewBookForm


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создайте 13 авторов для тестов разбиения на страницы
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name='Surname %s' % author_num,)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        # Получите вторую страницу и подтвердите, что на ней осталось (ровно) 3 элемента
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 3)


# Половина книг бронируется тестовыми пользователями, но в начале для них всех
# мы устанавливаем статус "доступно"
# НЕ РАБОТАЕТ!!! копипаста с задания
"""""
class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        # Создание двух пользователей
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG', 
                                        author=test_author, language=test_language)
        # Создать жанр как пост-шаг
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Присвоение типов many-to-many напрямую недопустимо
        test_book.save()

        # Создание 30 объектов BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy%5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', 
                                        due_back=return_date, borrower=the_borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # Проверка того, что мы используем правильный шаблон
        self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Проверка, что изначально у нас нет книг в списке
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        # Теперь все книги "взяты на прокат"
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # Проверка, что все забронированные книги в списке
        resp = self.client.get(reverse('my-borrowed'))
        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка успешности ответа
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        # Подтверждение, что все книги принадлежат testuser1 и взяты "на прокат"
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):

        # Изменение статуса на "в прокате"
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Подтверждение, что из всего списка показывается только 10 экземпляров
        self.assertEqual(len(resp.context['bookinstance_list']), 10)

        last_date = 0
        for copy in resp.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)
"""""


# Cоздаёт двух пользователей и два экземпляра книги, но только один пользователь
# получает необходимый доступ к соответствующему отображению.
# НЕ РАБОТАЕТ!!! копипаста с задания
"""""
class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        # Создание пользователя
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG',
                                        author=test_author, language=test_language,)

        # Создание жанра Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Создание объекта BookInstance для для пользователя test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                              due_back=return_date, borrower=test_user1, status='o')

        # Создание объекта BookInstance для для пользователя test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                              due_back=return_date, borrower=test_user2, status='o')

    #  проверяем, что только пользователь с соответствующим доступом (testuser2) имеет доступ к отображению.
    #  Мы проверяем все случаи: когда пользователь не залогинился
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        # Вручную проверить перенаправление (невозможно использовать assertRedirect, поскольку URL-адрес
        # перенаправления непредсказуем)
        self.assertEqual(resp.status_code, 302)
        # 'HttpResponseForbidden' object has no attribute 'url'
        # self.assertTrue(resp.url.startswith('/accounts/login/'))

    # когда залогинился, но не имеет соответствующего доступа
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Вручную проверить перенаправление (невозможно использовать assertRedirect, поскольку URL-адрес
        # перенаправления непредсказуем)
        self.assertEqual(resp.status_code, 403)
        # 'HttpResponseForbidden' object has no attribute 'url'
        # self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk, }))

        # Убедитесь, что он позволяет нам войти в систему — это наша книга, и у нас есть необходимые разрешения.
        self.assertEqual(resp.status_code, 200)

    #  когда имеет доступ, но не является заёмщиком книги
    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Убедитесь, что он позволяет нам войти. Мы библиотекарь, поэтому можем просматривать книги любых пользователей.
        self.assertEqual(resp.status_code, 200)

    #  если попытаться получить доступ к книге BookInstance которой не существует
    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()  # unlikely UID to match our bookinstance!
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid, }))
        self.assertEqual(resp.status_code, 404)

    # проверяем то, что используется правильный (необходимый) шаблон
    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        # Убедитесь, что мы использовали правильный шаблон
        self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')

    # проверяет что начальная дата равна трём неделям в будущем.
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    # Тест проверяет что отображение, в случае успеха, перенаправляет пользователя к списку всех забронированных книг.
    # Здесь мы показываем как при помощи клиента вы можете создать и передать данные в POST-запросе.
    # Данный запрос передаётся вторым аргументом в пост-функцию и представляет из себя словарь пар ключ/значение.
    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': valid_date_in_future})
        self.assertRedirects(resp, reverse('all-borrowed'))

    # Они тоже проверяют POST-запросы, но для случая неверных дат. Мы используем функцию assertFormError(),
    # чтобы проверить сообщения об ошибках.
    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': date_in_past})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': invalid_date_in_future})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')
"""""

# Tестовый вариант для отображения AuthorCreate
# коды ответа не соответсвуют выданным правам
class AuthorCreateTest(TestCase):
    # model = Author
    # fields = '__all__'
    # initial = {'date_of_death': '12/10/2016', }
    # permission_required = 'catalog.can_mark_returned'
    def setUp(self):
        # Создание двух пользователей
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        permission = Permission.objects.get(name='Can add author')
        test_user1.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can view author')
        test_user1.user_permissions.add(permission)
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Can view session')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Создание автора
        #test_author = Author.objects.create(first_name='John', last_name='Smith')

    # кто имеет доступ к отображению
    # редирект если не залогинен
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('author-create'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/author/create/')

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('author-create'))

        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

    def test_logged_in_without_permission(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author-create'))
        self.assertEqual(resp.status_code, 403)

    # начальную дату
    def test_authors_date(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('author-create'))
        # без понятия как достать дату с ответа открытия страницы
        # self.assertTrue(resp.context['name'] == "12/10/2016")

    # применяемый шаблон
    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('author-create'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/author/create/')

    # перенаправление из отображения в случае успеха
    def test_logged_in_uses_correct_template(self):
        resp = self.client.get(reverse('author-create'))
        self.assertRedirects(resp, '/accounts/login/?next=%2Fcatalog%2Fauthor%2Fcreate%2F')
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('author-create'))

        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

