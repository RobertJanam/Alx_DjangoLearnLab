from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Book

# TASK 3: Enforce permissions in views using decorators
# These views demonstrate how to use permission_required decorator

@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
    """
    View to display all books.
    Requires 'can_view' permission.
    """
    books = Book.objects.all()
    return render(request, 'bookshelf/book_list.html', {'books': books})

@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
def book_create(request):
    """
    View to create a new book.
    Requires 'can_create' permission.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        publication_year = request.POST.get('publication_year')

        if title and author and publication_year:
            Book.objects.create(
                title=title,
                author=author,
                publication_year=publication_year
            )
            messages.success(request, 'Book created successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please fill all fields.')

    return render(request, 'bookshelf/book_form.html', {'action': 'Create'})

@login_required
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, book_id):
    """
    View to edit an existing book.
    Requires 'can_edit' permission.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.publication_year = request.POST.get('publication_year')
        book.save()
        messages.success(request, 'Book updated successfully!')
        return redirect('book_list')

    return render(request, 'bookshelf/book_form.html', {'book': book, 'action': 'Edit'})

@login_required
@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, book_id):
    """
    View to delete a book.
    Requires 'can_delete' permission.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')

    return render(request, 'bookshelf/book_confirm_delete.html', {'book': book})

# Basic home view without permission requirement
def home(request):
    """
    Home page view - accessible to all users.
    """
    return render(request, 'bookshelf/home.html')