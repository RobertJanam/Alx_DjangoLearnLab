# Create Operation

```python
from bookshelf.models import Book

# Create a Book instance
book = Book.objects.create(
    title="1984",
    author="George Orwell",
    publication_year=1949
)

print(f"Created Book: {book.title} by {book.author} (ID: {book.id})")

#Created Book: 1984 by George Orwell