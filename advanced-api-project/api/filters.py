from django_filters import rest_framework as filters
from .models import Book, Author

class BookFilter(filters.FilterSet):
    # Basic filters
    title = filters.CharFilter(lookup_expr='icontains', help_text="Filter by title (case-insensitive partial match)")
    author = filters.NumberFilter(field_name='author__id', help_text="Filter by author ID")

    # Range filters
    publication_year = filters.NumberFilter(field_name='publication_year', help_text="Filter by exact publication year")
    publication_year__gt = filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='gt',
        help_text="Filter by publication year greater than"
    )
    publication_year__lt = filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='lt',
        help_text="Filter by publication year less than"
    )
    publication_year__gte = filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='gte',
        help_text="Filter by publication year greater than or equal to"
    )
    publication_year__lte = filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='lte',
        help_text="Filter by publication year less than or equal to"
    )

    # Date range filters
    created_at__gte = filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter by creation date greater than or equal to (YYYY-MM-DD)"
    )
    created_at__lte = filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter by creation date less than or equal to (YYYY-MM-DD)"
    )

    # Custom filter for year range
    publication_year_range = filters.RangeFilter(
        field_name='publication_year',
        help_text="Filter by publication year range (e.g., publication_year_range=1990&publication_year_range=2000)"
    )

    # Choice filter for publication year (dynamic choices)
    publication_year__in = filters.BaseInFilter(
        field_name='publication_year',
        help_text="Filter by multiple publication years (comma-separated)"
    )

    # Author name filter
    author_name = filters.CharFilter(
        field_name='author__name',
        lookup_expr='icontains',
        help_text="Filter by author name (case-insensitive partial match)"
    )

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'publication_year',
            'publication_year__gt', 'publication_year__lt',
            'publication_year__gte', 'publication_year__lte',
            'publication_year_range', 'publication_year__in',
            'author_name', 'created_at__gte', 'created_at__lte'
        ]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        decade = self.request.query_params.get('decade', None)
        if decade and decade.isdigit():
            decade = int(decade)
            queryset = queryset.filter(
                publication_year__gte=decade,
                publication_year__lt=decade + 10
            )

        return queryset


class AuthorFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', help_text="Filter by author name (case-insensitive)")
    has_books = filters.BooleanFilter(
        method='filter_has_books',
        help_text="Filter authors that have books (true) or no books (false)"
    )

    class Meta:
        model = Author
        fields = ['name', 'has_books']

    def filter_has_books(self, queryset, name, value):
        if value:
            return queryset.filter(books__isnull=False).distinct()
        else:
            return queryset.filter(books__isnull=True)