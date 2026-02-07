from django.urls import path
from . import views

urlpatterns = [
    # Book endpoints
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/create/', views.CustomBookCreateView.as_view(), name='book-create-custom'),
    path('books/<int:pk>/update/', views.CustomBookUpdateView.as_view(), name='book-update-custom'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete-custom'),

    # Author endpoints
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('authors/<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author-delete-custom'),

    # Custom view: Books by specific author
    path('authors/<int:author_id>/books/', views.BookByAuthorView.as_view(),
         name='books-by-author'),
]