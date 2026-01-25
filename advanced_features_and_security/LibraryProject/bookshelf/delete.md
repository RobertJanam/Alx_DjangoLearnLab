# Delete Operation

```python
from bookshelf.models import Book

all_books = Book.objects.all()

book = Book.objects.get(title="Nineteen Eighty-Four")
book_title = book.title
book_id = book.id

book.delete()

print("Book successfully deleted!")

# Book successfully deleted!