from django.shortcuts import render
from .models import Library, Book
from django.views.generic.detail import DetailView

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
