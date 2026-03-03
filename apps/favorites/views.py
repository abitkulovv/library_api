from rest_framework import viewsets, permissions
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