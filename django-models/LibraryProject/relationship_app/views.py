from django.shortcuts import render
from .models import Book, Library
from django.views.generic import DetailView

# Create your views here.
def display_all_books(request):
    all_books = Book.objects.all()
    context = {"all books" : all_books}

    return render(request, "relationship_app/list_book.html", context)

class Display_all_books_in_aLibrary(DetailView):
    model = Library

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        library = self.object
        context['books'] = library.books.all()

        return context
