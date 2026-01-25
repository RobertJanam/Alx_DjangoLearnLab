from django.urls import path
from . import views

# TASK 5: Documentation - URL patterns for book management with permission requirements
app_name = 'bookshelf'

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:book_id>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:book_id>/delete/', views.book_delete, name='book_delete'),
]