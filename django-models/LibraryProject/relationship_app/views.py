from django.shortcuts import render, redirect
from .models import Library, Book
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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