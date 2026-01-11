# Delete Operation

```python
from bookshelf.models import Book

all_books = Book.objects.all()

book_to_delete = Book.objects.get(title="Nineteen Eighty-Four")
book_title = book_to_delete.title
book_id = book_to_delete.id

book_to_delete.delete()

print("Book successfully deleted!")

# Book successfully deleted!