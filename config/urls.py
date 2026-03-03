from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    path("api/auth/", include("apps.users.urls")),
    path("api/authors/", include("apps.authors.urls")),
    path("api/books/", include("apps.books.urls")),
    path("api/favorites/", include("apps.favorites.urls")),
]