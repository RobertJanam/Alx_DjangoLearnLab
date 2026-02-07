from django.urls import path
from . import views

urlpatterns = [
    # Book endpoints - following the exact patterns required
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    path('books/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),

    # Author endpoints
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),

    # Custom view: Books by specific author
    path('authors/<int:author_id>/books/', views.BookByAuthorView.as_view(),
         name='books-by-author'),
]