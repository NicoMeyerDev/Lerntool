"""Zentrale URL-Konfiguration der Lern-App."""

from django.urls import include, path

urlpatterns = [
    path("api/", include("core.urls")),
    path("api/", include("lernen.urls")),
]
