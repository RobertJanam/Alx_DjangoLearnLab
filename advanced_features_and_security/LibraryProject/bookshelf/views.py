from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Book
from .forms import BookForm, SearchForm, ExampleForm  # Import the forms

# TASK 3: Enforce permissions in views using decorators
# These views demonstrate how to use permission_required decorator

@login_required
@permission_required('bookshelf.can_view', raise_exception=True)
def book_list(request):
    """
    View to display all books.
    Requires 'can_view' permission.
    SECURITY: Uses Django ORM to prevent SQL injection.
    """
    books = Book.objects.all().order_by('title')

    # SECURITY: Safe search functionality using Django ORM
    search_form = SearchForm(request.GET or None)
    if search_form.is_valid():
        query = search_form.cleaned_data['query']
        # SECURITY: Use Q objects for safe query building (prevents SQL injection)
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )

    return render(request, 'bookshelf/book_list.html', {
        'books': books,
        'search_form': search_form
    })

@login_required
@permission_required('bookshelf.can_create', raise_exception=True)
def book_create(request):
    """
    View to create a new book.
    Requires 'can_create' permission.
    SECURITY: Uses Django forms for validation and CSRF protection.
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # SECURITY: Form.save() uses parameterized queries to prevent SQL injection
            form.save()
            messages.success(request, 'Book created successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm()

    return render(request, 'bookshelf/book_form.html', {'form': form, 'action': 'Create'})

@login_required
@permission_required('bookshelf.can_edit', raise_exception=True)
def book_edit(request, book_id):
    """
    View to edit an existing book.
    Requires 'can_edit' permission.
    SECURITY: Uses get_object_or_404 for safe object retrieval.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            # SECURITY: Form.save() uses parameterized queries
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm(instance=book)

    return render(request, 'bookshelf/book_form.html', {'form': form, 'action': 'Edit'})

@login_required
@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, book_id):
    """
    View to delete a book.
    Requires 'can_delete' permission.
    SECURITY: Uses POST method for destructive actions.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # SECURITY: Only allow deletion via POST method
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')

    return render(request, 'bookshelf/book_confirm_delete.html', {'book': book})

# SECURITY: Example view demonstrating secure form handling
def form_example(request):
    """
    Example view demonstrating secure form handling practices.
    Includes CSRF protection, input validation, and XSS prevention.
    """
    if request.method == 'POST':
        form = ExampleForm(request.POST)
        if form.is_valid():
            # SECURITY: Process cleaned and validated data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # In a real application, you might save to database or send email
            # SECURITY: All data is already sanitized by the form

            messages.success(request, 'Form submitted successfully!')
            return redirect('form_example')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExampleForm()

    return render(request, 'bookshelf/form_example.html', {'form': form})

# SECURITY: Example of safe search using Django ORM
def safe_search_example(request):
    """
    Demonstrates safe search implementation using Django ORM.
    Prevents SQL injection by using parameterized queries.
    """
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # SECURITY: NEVER do this - vulnerable to SQL injection
        # BAD: Book.objects.raw(f"SELECT * FROM bookshelf_book WHERE title LIKE '%{query}%'")

        # SECURITY: DO THIS - safe using Django ORM
        results = Book.objects.filter(title__icontains=query)[:10]

    return render(request, 'bookshelf/safe_search.html', {
        'query': query,
        'results': results
    })

# Basic home view without permission requirement
def home(request):
    """
    Home page view - accessible to all users.
    SECURITY: No sensitive operations, simple render.
    """
    return render(request, 'bookshelf/home.html')