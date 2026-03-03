from rest_framework import serializers
from apps.books.models import Book
from apps.authors.models import Author
from apps.authors.serializers import AuthorSerializer


class BookSerializer(serializers.ModelSerializer):

    authors = AuthorSerializer(many=True, read_only=True)

    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        many=True,
        write_only=True,
        source="authors"
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "summary",
            "isbn",
            "publication_date",
            "genre",
            "created_at",
            "authors",
            "author_ids",
        )
        read_only_fields = ("created_at",)