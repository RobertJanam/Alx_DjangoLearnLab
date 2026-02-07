from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer, BookCreateSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
# Create your views here.

class BookListView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly | IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookCreateSerializer
        return BookSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # For POST requests, require authentication
            return [permissions.IsAuthenticated()]
        # For GET requests, allow anyone
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save()


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class AuthorListView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()


class BookByAuthorView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return Book.objects.filter(author_id=author_id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            author = get_object_or_404(Author, id=self.kwargs['author_id'])
            return Response({
                'author': author.name,
                'books': [],
                'message': f'No books found for author: {author.name}'
            })

        serializer = self.get_serializer(queryset, many=True)
        author = queryset.first().author
        response_data = {
            'author': author.name,
            'author_id': author.id,
            'books': serializer.data
        }
        return Response(response_data)

class CustomBookCreateView(generics.CreateAPIView):
    serializer_class = BookCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Perform additional validation if needed
            self.perform_custom_validation(serializer.validated_data)

            # Save the instance
            self.perform_create(serializer)

            # Create custom response
            headers = self.get_success_headers(serializer.data)
            response_data = {
                'status': 'success',
                'message': 'Book created successfully',
                'data': serializer.data,
                'book_id': serializer.instance.id
            }
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

        # Custom error response format
        return Response({
            'status': 'error',
            'message': 'Book creation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def perform_custom_validation(self, validated_data):
        pass

    def perform_create(self, serializer):
        serializer.save()


class CustomBookUpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            # Perform pre-update checks
            self.perform_pre_update_checks(instance, serializer.validated_data)

            # Perform the update
            self.perform_update(serializer)

            # Custom response format
            response_data = {
                'status': 'success',
                'message': 'Book updated successfully',
                'data': serializer.data
            }
            return Response(response_data)

        # Custom error response format
        return Response({
            'status': 'error',
            'message': 'Book update failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def perform_pre_update_checks(self, instance, validated_data):
        # Example -> Check if the publication year is being changed to an older year
        if 'publication_year' in validated_data:
            new_year = validated_data['publication_year']
            if new_year < instance.publication_year:
                raise PermissionDenied(
                    "Cannot change publication year to an earlier year"
                )

    def perform_update(self, serializer):
        serializer.save()

class BookDeleteView(generics.DestroyAPIView):
    """
    Custom DeleteView for Book model with additional functionality.

    This view demonstrates a standalone DeleteView with:
        - Custom delete logic
        - Pre-deletion checks
        - Custom response format
        - Additional security measures

    While BookDetailView already includes delete functionality,
    this separate view shows how to create a dedicated delete endpoint
    with custom behavior.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Store book info for response before deletion
        book_info = {
            'id': instance.id,
            'title': instance.title,
            'author': instance.author.name
        }

        self.perform_destroy(instance)

        return Response({
            'status': 'success',
            'message': 'Book deleted successfully',
            'deleted_book': book_info,
            'timestamp': instance.updated_at
        }, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        print(f"Deleting book: {instance.title} (ID: {instance.id})")
        instance.delete()


class AuthorDeleteView(generics.DestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if author has books
        book_count = instance.books.count()

        # Perform pre-deletion checks
        self.perform_pre_delete_checks(instance, book_count)

        # Store author info for response
        author_info = {
            'id': instance.id,
            'name': instance.name,
            'book_count': book_count
        }

        # If author has books, store book info
        books_info = []
        if book_count > 0:
            books_info = [
                {'id': book.id, 'title': book.title}
                for book in instance.books.all()
            ]

        # Perform the deletion (this will cascade delete books)
        self.perform_destroy(instance)

        # Custom success response
        response_data = {
            'status': 'success',
            'message': 'Author deleted successfully',
            'deleted_author': author_info,
        }

        if books_info:
            response_data['cascade_deleted_books'] = books_info
            response_data['message'] += f' along with {book_count} related book(s)'

        return Response(response_data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        # Log the deletion
        print(f"Deleting author: {instance.name} (ID: {instance.id})")

        # Delete the author (books will be cascade deleted)
        instance.delete()