from rest_framework import serializers
from apps.favorites.models import Favorite
from apps.books.serializers import BookSerializer
from apps.books.models import Book


class FavoriteSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), write_only=True, source="book"
    )

    class Meta:
        model = Favorite
        fields = ("id", "book", "book_id", "added_at")
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=["user", "book"],
                message="This book is already in favorites for this user."
            )
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return Favorite.objects.create(user=user, **validated_data)