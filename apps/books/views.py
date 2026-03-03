from rest_framework import viewsets, permissions
from apps.books.models import Book
from apps.books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.prefetch_related("authors").all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]