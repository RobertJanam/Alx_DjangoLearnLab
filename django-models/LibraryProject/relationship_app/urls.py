from . import views
from django.urls import path
from .views import list_books, LibraryDetailView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('books/', views.list_books, name='list_books'),
    path('library/<int:pk>/', LibraryDetailView.as_view('relationship_app/library_detail.html'), name='library_detail'),
    path('login/', LoginView.as_view('relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view('relationship_app/logout.html'), name='logout'),
    path('register/', views.register, name="register"),

]