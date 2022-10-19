from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language

admin.site.register(Genre)
admin.site.register(Language)


class BooksInline(admin.TabularInline):
    """Определяет формат встроенной вставки книги (используется в AuthorAdmin)"""
    model = Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Объект администрирования для авторских моделей.
    Определяет:
    - поля, которые будут отображаться в виде списка (list_display)
    - поля заказов в детальном представлении (fields),
    группирующие поля даты по горизонтали
    - добавляет встроенное добавление книг в представлении автора (inlines)
    """
    list_display = ('last_name',
                    'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]


class BooksInstanceInline(admin.TabularInline):
    """Определяет формат вставки встроенного экземпляра книги (используется в BookAdmin)"""
    model = BookInstance


class BookAdmin(admin.ModelAdmin):
    """
    Объект администрирования для книжных моделей.
    Определяет:
    - поля, которые будут отображаться в виде списка (list_display)
    - добавляет встроенное добавление экземпляров книги в просмотр книги (inlines)
    """
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


admin.site.register(Book, BookAdmin)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    """Объект администрирования для моделей BookInstance.
    Определяет:
    - поля, которые будут отображаться в виде списка (list_display)
    - фильтры, которые будут отображаться на боковой панели (list_filter)
    - группировка полей в разделы (fieldsets)
    """
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
