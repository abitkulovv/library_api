from rest_framework import serializers
from apps.books.models import Book
from apps.authors.serializers import AuthorSerializer
from apps.authors.models import Author

class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), many=True, write_only=True, source="authors"
    )

    class Meta:
        model = Book
        fields = ("id", "title", "description", "publication_date", "authors", "author_ids")