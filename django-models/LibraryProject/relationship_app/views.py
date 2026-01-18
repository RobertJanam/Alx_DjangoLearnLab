from django.shortcuts import render, redirect, get_object_or_404
from .models import Library, Book, Author, UserProfile
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import BookForm

# Helper functions for role checking
def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

def is_librarian(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'librarian'

def is_member(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'member'

# Create your views here.
def list_books(request):
    all_books = Book.objects.all()
    context = {"all_books": all_books}
    return render(request, "relationship_app/list_books.html", context)

class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library = self.object
        context['books'] = library.books.all()
        return context

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('list_books')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'relationship_app/register.html', context)

@login_required
@user_passes_test(is_admin)
def admin_view(request):
    context = {
        'user': request.user,
        'role': request.user.profile.get_role_display()
    }
    return render(request, 'relationship_app/admin_view.html', context)

@login_required
@user_passes_test(is_librarian)
def librarian_view(request):
    libraries = Library.objects.all()
    context = {
        'user': request.user,
        'role': request.user.profile.get_role_display(),
        'libraries': libraries
    }
    return render(request, 'relationship_app/librarian_view.html', context)

@login_required
@user_passes_test(is_member)
def member_view(request):
    books = Book.objects.all()
    context = {
        'user': request.user,
        'role': request.user.profile.get_role_display(),
        'books': books
    }
    return render(request, 'relationship_app/member_view.html', context)

@login_required
@permission_required('relationship_app.can_add_book', raise_exception=True)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('list_books')
    else:
        form = BookForm()

    context = {'form': form, 'action': 'Add'}
    return render(request, 'relationship_app/book_form.html', context)

@login_required
@permission_required('relationship_app.can_change_book', raise_exception=True)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('list_books')
    else:
        form = BookForm(instance=book)

    context = {'form': form, 'action': 'Edit', 'book': book}
    return render(request, 'relationship_app/book_form.html', context)

@login_required
@permission_required('relationship_app.can_delete_book', raise_exception=True)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted successfully!')
        return redirect('list_books')

    context = {'book': book}
    return render(request, 'relationship_app/delete_book.html', context)