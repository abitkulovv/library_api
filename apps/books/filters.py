import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    publication_date = django_filters.DateFromToRangeFilter()
    authors = django_filters.NumberFilter(field_name="authors__id")
    genre = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Book
        fields = ["authors", "genre", "publication_date"]