from django.urls import path
from apps.users.views import UserRegisterView, UserProfileView
from apps.users.views import LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", UserRegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("profile/", UserProfileView.as_view()),
    path("logout/", LogoutView.as_view()),
]