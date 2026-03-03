from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.books.models import Book
from apps.books.serializers import BookSerializer
from apps.books.filters import BookFilter


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.prefetch_related("authors").all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    search_fields = ["title", "authors__last_name"]
    ordering_fields = ["publication_date", "authors__last_name", "genre"]