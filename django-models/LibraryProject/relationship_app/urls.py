from . import views
from django.urls import path
from .views import list_books, LibraryDetailView, admin_view, librarian_view, member_view
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'relationship_app'

urlpatterns = [
    path('books/', views.list_books, name='list_books'),
    path('library/<int:pk>/', LibraryDetailView.as_view(template_name='relationship_app/library_detail.html'), name='library_detail'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('register/', views.register, name="register"),
    path('admin-dashboard/', admin_view, name='admin_view'),
    path('librarian-dashboard/', librarian_view, name='librarian_view'),
    path('member-dashboard/', member_view, name='member_view'),
]