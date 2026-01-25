from django import forms
from .models import Book, Author

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Book Title',
            'author': 'Author',
        }