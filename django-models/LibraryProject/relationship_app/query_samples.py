from .models import *

# query all books by a specific author
get_author = Author.objects.get(name="Author name")
print(f"Author: {get_author}")

all_books_by_author = get_author.books.all()
print(all_books_by_author)

# list all books in a library
library = Library.objects.get(name="library name")

get_all_books = library.books.all()

print(f"\nBooks in {library}\n")
print(get_all_books)

# retrieve the librarian for a library
get_library = Library.objects.get(library="library name")

librarian = library.librarian

print(f"{librarian} is the librarian of {library}")