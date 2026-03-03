from rest_framework import serializers
from apps.favorites.models import Favorite
from apps.books.models import Book
from apps.books.serializers import BookSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        write_only=True,
        source="book"
    )

    class Meta:
        model = Favorite
        fields = (
            "id",
            "book",
            "book_id",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        user = self.context["request"].user
        book = attrs["book"]

        if Favorite.objects.filter(user=user, book=book).exists():
            raise serializers.ValidationError("Book already in favorites.")

        return attrs

    def create(self, validated_data):
        return Favorite.objects.create(
            user=self.context["request"].user,
            book=validated_data["book"],
        )