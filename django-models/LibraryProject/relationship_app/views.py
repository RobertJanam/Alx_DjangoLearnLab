from django.shortcuts import render, redirect
from .models import Library, Book, UserProfile
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

def is_librarian(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'librarian'

def is_member(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'member'

# Create your views here.
def list_books(request):
    all_books = Book.objects.all()
    context = {"all books": all_books}

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
            return redirect('relationship_app:list_books')

    else:
        form = UserCreationForm()

    context = {'form': form}

    return render(request, 'relationship_app/register.html', context)

# Role-based views
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
    # Librarians can see all libraries
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
    # Members can see available books
    books = Book.objects.all()
    context = {
        'user': request.user,
        'role': request.user.profile.get_role_display(),
        'books': books
    }
    return render(request, 'relationship_app/member_view.html', context)
