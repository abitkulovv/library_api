from rest_framework.routers import DefaultRouter
from apps.favorites.views import FavoriteViewSet

router = DefaultRouter()
router.register("", FavoriteViewSet, basename="favorites")

urlpatterns = router.urls