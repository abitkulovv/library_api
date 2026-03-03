from rest_framework import serializers
from apps.authors.models import Author


class AuthorSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Author
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "biography",
            "date_of_birth",
            "date_of_death",
        )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"