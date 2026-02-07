from rest_framework import serializers
from django.utils import timezone
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    #Serializer for the Book model.
    #serialization and deserialization of Book instances with custom validation.
    #Includes validation to ensure publication_year is not in the future.

    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_publication_year(self, value):
        # Validate that the publication year is not in the future.
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value

    def validate(self, data):
        if 'title' in data:
            if not data['title'].strip():
                raise serializers.ValidationError({
                    'title': 'Title cannot be empty or consist only of whitespace.'
                })
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model with nested Book serialization.

    This one handles serialization of Author instances including their related Book instances.
    The 'books' field uses BookSerializer to serialize all related books.

    The attributes:
        books: Nested BookSerializer for handling related books.
        model: The Author model class that this serializer works with.
        fields: List of fields to include in serialization.
        read_only_fields: Fields that should be read-only (not editable).
    """
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """
        Validate the author's name.

        Args:
            value (str): The author's name to validate.

        Returns:
            str: The validated name.

        Raises:
            serializers.ValidationError: If the name is empty or too short.
        """
        if not value.strip():
            raise serializers.ValidationError("Author name cannot be empty.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Author name must be at least 2 characters long.")
        return value.strip()


class BookCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating Book instances.

    This serializer doesn't include nested relationships and is optimized
    for create operations where we just need the author's ID.
    """
    class Meta:
        model = Book
        fields = ['title', 'publication_year', 'author']

    def validate_publication_year(self, value):
        # Reuse validation from BookSerializer
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value