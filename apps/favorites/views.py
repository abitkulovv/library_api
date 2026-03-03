from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.favorites.models import Favorite
from apps.favorites.serializers import FavoriteSerializer
from apps.favorites.permissions import IsOwner


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return (
            Favorite.objects
            .select_related("book")
            .prefetch_related("book__authors")
            .filter(user=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["delete"], url_path="clear")
    def clear(self, request):
        deleted_count, _ = self.get_queryset().delete()
        return Response(
            {"deleted": deleted_count},
            status=status.HTTP_204_NO_CONTENT,
        )