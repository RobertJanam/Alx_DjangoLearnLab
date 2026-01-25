from django import forms
from django.core.exceptions import ValidationError
from .models import Book
import bleach  # For HTML sanitization


class BookForm(forms.ModelForm):
    """
    Secure form for creating and editing books.
    Includes input validation and sanitization to prevent security vulnerabilities.
    """

    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name'
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter publication year',
                'min': '1000',
                'max': '2100'
            }),
        }

    def clean_title(self):
        """
        Sanitize and validate the title field.
        Prevents XSS by removing potentially dangerous HTML/JavaScript.
        """
        title = self.cleaned_data.get('title', '')
        # Sanitize HTML to prevent XSS
        clean_title = bleach.clean(
            title,
            tags=[],  # No HTML tags allowed
            attributes={},
            strip=True
        )

        # Additional validation
        if len(clean_title) < 2:
            raise ValidationError("Title must be at least 2 characters long.")
        if len(clean_title) > 200:
            raise ValidationError("Title cannot exceed 200 characters.")

        return clean_title

    def clean_author(self):
        """
        Sanitize and validate the author field.
        """
        author = self.cleaned_data.get('author', '')
        # Sanitize HTML to prevent XSS
        clean_author = bleach.clean(
            author,
            tags=[],  # No HTML tags allowed
            attributes={},
            strip=True
        )

        if len(clean_author) < 2:
            raise ValidationError("Author name must be at least 2 characters long.")
        if len(clean_author) > 100:
            raise ValidationError("Author name cannot exceed 100 characters.")

        return clean_author

    def clean_publication_year(self):
        """
        Validate publication year to prevent invalid data.
        """
        year = self.cleaned_data.get('publication_year')

        if year is not None:
            if year < 1000 or year > 2100:
                raise ValidationError("Publication year must be between 1000 and 2100.")

        return year


class SearchForm(forms.Form):
    """
    Secure search form with input validation.
    Demonstrates safe handling of user input for search functionality.
    """
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search books...'
        })
    )

    def clean_query(self):
        """
        Sanitize search query to prevent SQL injection and XSS.
        """
        query = self.cleaned_data.get('query', '')
        # Sanitize HTML to prevent XSS
        clean_query = bleach.clean(
            query,
            tags=[],  # No HTML tags allowed
            attributes={},
            strip=True
        )

        # Remove SQL injection patterns (basic example)
        sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', 'UNION', ';', '--']
        for keyword in sql_keywords:
            if keyword.lower() in clean_query.lower():
                raise ValidationError(f"Search query contains invalid characters: {keyword}")

        if len(clean_query) > 100:
            raise ValidationError("Search query cannot exceed 100 characters.")

        return clean_query


class ExampleForm(forms.Form):
    """
    Example form for demonstrating security best practices.
    Shows proper form validation and CSRF protection.
    """
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name'
        }),
        help_text="Enter your name (2-100 characters)"
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        }),
        help_text="Enter a valid email address"
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your message',
            'rows': 4
        }),
        help_text="Enter your message (10-1000 characters)"
    )

    def clean_name(self):
        """Validate and sanitize the name field."""
        name = self.cleaned_data.get('name', '')
        clean_name = bleach.clean(name, tags=[], attributes={}, strip=True)

        if len(clean_name) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        if len(clean_name) > 100:
            raise ValidationError("Name cannot exceed 100 characters.")

        return clean_name

    def clean_message(self):
        """Validate and sanitize the message field."""
        message = self.cleaned_data.get('message', '')
        clean_message = bleach.clean(
            message,
            tags=['b', 'i', 'u', 'p', 'br'],  # Allow only basic formatting tags
            attributes={},
            strip=True
        )

        if len(clean_message) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        if len(clean_message) > 1000:
            raise ValidationError("Message cannot exceed 1000 characters.")

        return clean_message