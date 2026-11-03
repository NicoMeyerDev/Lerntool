"""URLs der Kern-App unterhalb von `/api/`."""

from django.urls import path

from core.auth_views import IchView, LoginView, LogoutView
from core.views import HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/ich/", IchView.as_view(), name="ich"),
]
