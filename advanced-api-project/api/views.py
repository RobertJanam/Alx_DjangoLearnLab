"""
Views for the API application using Django REST Framework's generic views.

This module implements custom views and generic views for handling CRUD operations
on Book and Author models with proper permissions and custom behavior.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer, BookCreateSerializer
from .filters import BookFilter, AuthorFilter


class BookListView(generics.ListAPIView):
    """
    List all books with advanced filtering, searching, and ordering capabilities.

    GET: Returns a list of all Book instances with support for:
        - Filtering by title, author, publication year, date ranges
        - Searching in title and author name fields
        - Ordering by any field (default: title)
        - Pagination (10 items per page)

    Query Parameters:
        - Filtering:
            ?title=harry          # Books with 'harry' in title (case-insensitive)
            ?author=1             # Books by author ID 1
            ?author_name=rowling  # Books by author with 'rowling' in name
            ?publication_year=1997 # Books published in 1997
            ?publication_year__gt=1990&publication_year__lt=2000 # Books between 1990 and 2000
            ?publication_year_range=1990&publication_year_range=2000 # Same as above
            ?created_at__gte=2024-01-01 # Books created since Jan 1, 2024
        - Searching:
            ?search=harry         # Search in title and author name
        - Ordering:
            ?ordering=title       # Sort by title ascending
            ?ordering=-title      # Sort by title descending
            ?ordering=publication_year,-title # Multiple fields
        - Pagination:
            ?page=2               # Page 2 of results
            ?page_size=20         # 20 items per page

    Permissions: AllowAny (anyone can view books)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

    # Filter, search, and ordering backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filter configuration
    filterset_class = BookFilter

    # Search configuration - search in title and author name
    search_fields = ['title', 'author__name']

    # Ordering configuration - allow ordering by any field
    ordering_fields = [
        'id', 'title', 'publication_year',
        'created_at', 'updated_at', 'author__name'
    ]
    ordering = ['title']  # Default ordering

    # Pagination is handled by REST_FRAMEWORK settings

    def get_queryset(self):
        """
        Override get_queryset to add custom filtering logic.

        Returns:
            QuerySet: The filtered, searched, and ordered queryset.
        """
        queryset = super().get_queryset()

        # Additional custom filtering can be added here
        # Example: Filter by minimum publication year if specified
        min_year = self.request.query_params.get('min_year')
        if min_year and min_year.isdigit():
            queryset = queryset.filter(publication_year__gte=int(min_year))

        # Example: Filter by maximum publication year if specified
        max_year = self.request.query_params.get('max_year')
        if max_year and max_year.isdigit():
            queryset = queryset.filter(publication_year__lte=int(max_year))

        return queryset.select_related('author')

    def list(self, request, *args, **kwargs):
        """
        Override list method to include filtering metadata in response.

        Returns:
            Response: List of books with filtering metadata.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'books': serializer.data,
                'filters_applied': self.get_applied_filters(),
                'total_count': queryset.count(),
                'search_query': request.query_params.get('search', ''),
                'ordering': request.query_params.get('ordering', 'title (default)')
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'books': serializer.data,
            'filters_applied': self.get_applied_filters(),
            'total_count': queryset.count(),
            'search_query': request.query_params.get('search', ''),
            'ordering': request.query_params.get('ordering', 'title (default)')
        })

    def get_applied_filters(self):
        """
        Get a dictionary of applied filters from the request.

        Returns:
            dict: Applied filters and their values.
        """
        applied_filters = {}

        # Get filter fields from filterset
        filter_fields = self.filterset_class.Meta.fields

        for field in filter_fields:
            value = self.request.query_params.get(field)
            if value is not None:
                applied_filters[field] = value

        # Also check for search and ordering
        search = self.request.query_params.get('search')
        ordering = self.request.query_params.get('ordering')

        if search:
            applied_filters['search'] = search
        if ordering:
            applied_filters['ordering'] = ordering

        return applied_filters


class BookCreateView(generics.CreateAPIView):
    """
    Create a new book.

    POST: Creates a new Book instance with data validation.

    Permissions: IsAuthenticated (only authenticated users can create books)
    """
    serializer_class = BookCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Override create method to provide custom response format.

        Returns:
            Response: Custom response with additional metadata.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Save the book instance."""
        serializer.save()


class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book.

    PUT: Update a book by ID (full update).
    PATCH: Update a book by ID (partial update).

    Permissions: IsAuthenticated (only authenticated users can update books)
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Get the book object based on ID provided in request data.

        Returns:
            Book: The book instance to update.

        Raises:
            Http404: If book with given ID doesn't exist.
        """
        book_id = self.request.data.get('id')
        if not book_id:
            raise Http404("Book ID is required in request data")

        # Get the book object
        book = get_object_or_404(Book, id=book_id)

        # Check object permissions
        self.check_object_permissions(self.request, book)

        return book

    def update(self, request, *args, **kwargs):
        """
        Override update method to provide custom behavior.

        Returns:
            Response: Custom response with additional metadata.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            # Perform pre-update checks
            self.perform_pre_update_checks(instance, serializer.validated_data)

            # Perform the update
            self.perform_update(serializer)

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_pre_update_checks(self, instance, validated_data):
        """
        Perform checks before updating the book.

        Args:
            instance: The book instance being updated.
            validated_data (dict): The validated update data.

        Raises:
            PermissionDenied: If checks fail.
        """
        # Example: Check if the publication year is being changed to an older year
        if 'publication_year' in validated_data:
            new_year = validated_data['publication_year']
            if new_year < instance.publication_year:
                raise PermissionDenied(
                    "Cannot change publication year to an earlier year"
                )

    def perform_update(self, serializer):
        """
        Save the updated book instance.

        Args:
            serializer: The serializer instance.
        """
        serializer.save()


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book.

    DELETE: Delete a book by ID.

    Permissions: IsAuthenticated (only authenticated users can delete books)
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Get the book object based on ID provided in request data.

        Returns:
            Book: The book instance to delete.

        Raises:
            Http404: If book with given ID doesn't exist.
        """
        book_id = self.request.data.get('id')
        if not book_id:
            raise Http404("Book ID is required in request data")

        # Get the book object
        book = get_object_or_404(Book, id=book_id)

        # Check object permissions
        self.check_object_permissions(self.request, book)

        return book

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to provide custom behavior.

        Returns:
            Response: Custom response with deletion confirmation.
        """
        instance = self.get_object()

        # Perform pre-deletion checks
        self.perform_pre_delete_checks(instance)

        # Perform the deletion
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_pre_delete_checks(self, instance):
        """
        Perform checks before deleting the book.

        Args:
            instance: The book instance being deleted.

        Raises:
            PermissionDenied: If checks fail.
        """
        # Example: Prevent deletion of books published in the last year
        from django.utils import timezone
        current_year = timezone.now().year

        if instance.publication_year >= current_year - 1:
            raise PermissionDenied(
                f"Cannot delete books published in the last year "
                f"(published in {instance.publication_year})"
            )

    def perform_destroy(self, instance):
        """
        Delete the book instance.

        Args:
            instance: The book instance to delete.
        """
        instance.delete()


class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific book instance.

    GET: Retrieve a specific book by ID.

    Permissions: AllowAny (anyone can view a book)
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]


class AuthorListView(generics.ListCreateAPIView):
    """
    List all authors or create a new author with filtering capabilities.

    GET: Returns a list of all Author instances with their books.
        Supports filtering by name and has_books.
    POST: Creates a new Author instance with data validation.

    Permissions:
        - GET: AllowAny (anyone can view authors)
        - POST: IsAuthenticated (only authenticated users can create authors)
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Add filtering capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuthorFilter
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_create(self, serializer):
        """Save the author instance."""
        serializer.save()


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific author instance.

    GET: Retrieve a specific author by ID with nested books.
    PUT: Update a specific author by ID (full update).
    PATCH: Update a specific author by ID (partial update).
    DELETE: Delete a specific author by ID (cascades to delete related books).

    Permissions:
        - GET: AllowAny (anyone can view an author)
        - PUT/PATCH/DELETE: IsAuthenticated (only authenticated users can modify authors)
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        """Save the updated author instance."""
        serializer.save()

    def perform_destroy(self, instance):
        """Delete the author instance (related books will cascade delete)."""
        instance.delete()


class BookByAuthorView(generics.ListAPIView):
    """
    Custom view to list all books by a specific author with filtering capabilities.

    GET: Returns a list of all books written by a specific author.
        Supports filtering, searching, and ordering on the books.

    Permissions: AllowAny (anyone can view books by author)

    This is a custom view that extends functionality beyond basic CRUD operations.
    """
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

    # Add filtering capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title']
    ordering_fields = ['title', 'publication_year']
    ordering = ['title']

    def get_queryset(self):
        """
        Custom queryset to filter books by author ID from URL parameter.

        Returns:
            QuerySet: Books filtered by the specified author ID.
        """
        author_id = self.kwargs['author_id']
        return Book.objects.filter(author_id=author_id).select_related('author')

    def list(self, request, *args, **kwargs):
        """
        Override the list method to include author information in response.

        Returns:
            Response: List of books with author context.
        """
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
            'total_books': queryset.count(),
            'books': serializer.data,
            'filters_applied': {
                'author_id': author_id,
                'search': request.query_params.get('search', ''),
                'ordering': request.query_params.get('ordering', 'title (default)')
            }
        }
        return Response(response_data)