from django.contrib import admin

# Register your models here.
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('author', 'publication_year')
    raw_id_fields = ('author',)