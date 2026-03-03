from rest_framework.routers import DefaultRouter
from apps.authors.views import AuthorViewSet

router = DefaultRouter()
router.register("", AuthorViewSet, basename="authors")

urlpatterns = router.urls