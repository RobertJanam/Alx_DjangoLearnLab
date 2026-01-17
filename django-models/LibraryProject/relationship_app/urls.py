from . import views
from django.urls import path
from .views import Display_all_books_in_aLibrary

urlpatterns = [
    path('books/', views.display_all_books, name='list_books'),
    path('library/<int:pk>/', Display_all_books_in_aLibrary.as_view, name='library_detail')

]