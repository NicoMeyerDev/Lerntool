"""URLs der Lern-API unterhalb von `/api/`."""

from django.urls import path

from lernen import views

urlpatterns = [
    path("themen/", views.ThemaListeView.as_view(), name="themen"),
    path("themen/<slug:slug>/", views.ThemaDetailView.as_view(), name="thema"),
    path("lektionen/<int:pk>/", views.LektionDetailView.as_view(), name="lektion"),
    path("quizze/<int:pk>/", views.QuizDetailView.as_view(), name="quiz"),
    path("quizze/<int:pk>/abgabe/", views.QuizAbgabeView.as_view(), name="quiz-abgabe"),
    path("tests/<int:pk>/", views.TestDetailView.as_view(), name="test"),
    path("tests/<int:pk>/start/", views.TestStartView.as_view(), name="test-start"),
    path("tests/<int:pk>/abgabe/", views.TestAbgabeView.as_view(), name="test-abgabe"),
    path("projekte/<int:pk>/", views.ProjektDetailView.as_view(), name="projekt"),
    path(
        "projekte/<int:pk>/punkte/<int:punkt_id>/",
        views.ProjektPunktView.as_view(),
        name="projekt-punkt",
    ),
    path(
        "abschnitte/<int:pk>/gelesen/",
        views.AbschnittGelesenView.as_view(),
        name="abschnitt-gelesen",
    ),
    path("fortschritt/", views.FortschrittListeView.as_view(), name="fortschritt"),
]
