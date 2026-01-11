# Retrieve Operation

```python
from bookshelf.models import Book

book_class = Book.objects.all()

for book in book_class:
    print(f"Title: {book.title}\n"
    f"Author: {book.author}\n"
    f"Publication Year: {book.publication_year}\n")

# Title: 1984
# Author: George Orwell
# Publication Year: 1949