# Update Operation

```python
from bookshelf.models import Book

book_class = Book.objects.get(title="1984")

book_class.title = "Nineteen Eighty-Four"

book.save()

updated_book = Book.objects.get(id=book.id)
print(f"Updated Title: {updated_book.title}")

# Updated Title: Nineteen Eighty-Four