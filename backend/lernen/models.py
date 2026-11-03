"""Datenmodell für Lerninhalte und Lernfortschritt.

Aufbau der Inhalte (siehe docs/ENTSCHEIDUNGEN.md, Abschnitt B1):

    Thema → Phase → Lektion (= Themenfeld) → Abschnitt
    Abschnitt 1:1 Quiz        (Quiz nach jedem Abschnitt)
    Lektion   1:1 Test        (Test nach jedem Themenfeld, max. 30 Minuten)
    Phase     1:n Projektaufgabe
    Quiz/Test 1:n Frage 1:n Antwort (höchstens eine richtig; „mindestens eine“
                                     prüft der spätere Import der Inhalte)
    Lektion   1:n Quelle      (Quellenangaben mit Link)

Fortschritt speichert pro Nutzer, was erledigt ist und mit welchem Ergebnis.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q

#: Obergrenze für die Dauer eines Tests in Minuten (CLAUDE.md, Abschnitt 5).
TEST_MAX_MINUTEN = 30


class Thema(models.Model):
    """Oberstes Lerngebiet, z. B. „PHP/Laravel“ oder „Englisch“."""

    titel = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    beschreibung = models.TextField(blank=True)
    reihenfolge = models.PositiveIntegerField(unique=True)

    class Meta:
        """Sortierung und Anzeigenamen."""

        ordering = ["reihenfolge"]
        verbose_name = "Thema"
        verbose_name_plural = "Themen"

    def __str__(self) -> str:
        """Gibt den Titel zurück."""
        return self.titel


class Phase(models.Model):
    """Abschnitt eines Themas, z. B. „PHP-Basics“ im Thema PHP/Laravel."""

    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, related_name="phasen")
    titel = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    beschreibung = models.TextField(blank=True)
    reihenfolge = models.PositiveIntegerField()

    class Meta:
        """Sortierung, Eindeutigkeit innerhalb des Themas und Anzeigenamen."""

        ordering = ["thema__reihenfolge", "reihenfolge"]
        verbose_name = "Phase"
        verbose_name_plural = "Phasen"
        constraints = [
            models.UniqueConstraint(
                fields=["thema", "reihenfolge"], name="phase_reihenfolge_je_thema"
            ),
            models.UniqueConstraint(fields=["thema", "slug"], name="phase_slug_je_thema"),
        ]

    def __str__(self) -> str:
        """Gibt den Titel zurück."""
        return self.titel


class Lektion(models.Model):
    """Ein Themenfeld innerhalb einer Phase, z. B. „Arrays“. Endet mit einem Test."""

    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name="lektionen")
    titel = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    zusammenfassung = models.TextField(blank=True)
    reihenfolge = models.PositiveIntegerField()

    class Meta:
        """Sortierung, Eindeutigkeit innerhalb der Phase und Anzeigenamen."""

        ordering = ["phase__thema__reihenfolge", "phase__reihenfolge", "reihenfolge"]
        verbose_name = "Lektion"
        verbose_name_plural = "Lektionen"
        constraints = [
            models.UniqueConstraint(
                fields=["phase", "reihenfolge"], name="lektion_reihenfolge_je_phase"
            ),
            models.UniqueConstraint(fields=["phase", "slug"], name="lektion_slug_je_phase"),
        ]

    def __str__(self) -> str:
        """Gibt den Titel zurück."""
        return self.titel


class Quelle(models.Model):
    """Quellenangabe einer Lektion mit Link (Pflicht laut CLAUDE.md, Abschnitt 5)."""

    lektion = models.ForeignKey(Lektion, on_delete=models.CASCADE, related_name="quellen")
    titel = models.CharField(max_length=300)
    url = models.URLField(max_length=500)

    class Meta:
        """Anzeigenamen und Eindeutigkeit des Links je Lektion."""

        verbose_name = "Quelle"
        verbose_name_plural = "Quellen"
        constraints = [
            models.UniqueConstraint(fields=["lektion", "url"], name="quelle_url_je_lektion"),
        ]

    def __str__(self) -> str:
        """Gibt Titel und Link zurück."""
        return f"{self.titel} ({self.url})"


class Abschnitt(models.Model):
    """Ein kurzer Lernschritt einer Lektion. Inhalt als Markdown. Endet mit einem Quiz."""

    lektion = models.ForeignKey(Lektion, on_delete=models.CASCADE, related_name="abschnitte")
    titel = models.CharField(max_length=200)
    inhalt = models.TextField(help_text="Lerntext als Markdown.")
    reihenfolge = models.PositiveIntegerField()

    class Meta:
        """Sortierung, Eindeutigkeit innerhalb der Lektion und Anzeigenamen."""

        ordering = ["lektion", "reihenfolge"]
        verbose_name = "Abschnitt"
        verbose_name_plural = "Abschnitte"
        constraints = [
            models.UniqueConstraint(
                fields=["lektion", "reihenfolge"], name="abschnitt_reihenfolge_je_lektion"
            ),
        ]

    def __str__(self) -> str:
        """Gibt den Titel zurück."""
        return self.titel


class Quiz(models.Model):
    """Kurzes Quiz am Ende eines Abschnitts."""

    abschnitt = models.OneToOneField(Abschnitt, on_delete=models.CASCADE, related_name="quiz")

    class Meta:
        """Anzeigenamen."""

        verbose_name = "Quiz"
        verbose_name_plural = "Quizze"

    def __str__(self) -> str:
        """Gibt den Abschnitt an, zu dem das Quiz gehört."""
        return f"Quiz: {self.abschnitt.titel}"


class Test(models.Model):
    """Test am Ende einer Lektion (Themenfeld) mit Zeitlimit von höchstens 30 Minuten."""

    lektion = models.OneToOneField(Lektion, on_delete=models.CASCADE, related_name="test")
    zeitlimit_minuten = models.PositiveSmallIntegerField(
        default=TEST_MAX_MINUTEN,
        validators=[MinValueValidator(1), MaxValueValidator(TEST_MAX_MINUTEN)],
    )

    class Meta:
        """Anzeigenamen und Grenzen des Zeitlimits."""

        verbose_name = "Test"
        verbose_name_plural = "Tests"
        constraints = [
            models.CheckConstraint(
                condition=Q(zeitlimit_minuten__gte=1, zeitlimit_minuten__lte=TEST_MAX_MINUTEN),
                name="test_zeitlimit_1_bis_30",
            ),
        ]

    def __str__(self) -> str:
        """Gibt die Lektion an, zu der der Test gehört."""
        return f"Test: {self.lektion.titel}"


class Frage(models.Model):
    """Frage mit Antwortmöglichkeiten. Gehört entweder zu einem Quiz oder zu einem Test."""

    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, null=True, blank=True, related_name="fragen"
    )
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, null=True, blank=True, related_name="fragen"
    )
    text = models.TextField()
    erklaerung = models.TextField(
        blank=True, help_text="Kurze Begründung der richtigen Antwort für die Auswertung."
    )
    reihenfolge = models.PositiveIntegerField()

    class Meta:
        """Sortierung, Zuordnung zu genau einem Quiz oder Test und Anzeigenamen."""

        ordering = ["reihenfolge"]
        verbose_name = "Frage"
        verbose_name_plural = "Fragen"
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(quiz__isnull=False, test__isnull=True)
                    | Q(quiz__isnull=True, test__isnull=False)
                ),
                name="frage_gehoert_zu_quiz_oder_test",
            ),
            models.UniqueConstraint(
                fields=["quiz", "reihenfolge"], name="frage_reihenfolge_je_quiz"
            ),
            models.UniqueConstraint(
                fields=["test", "reihenfolge"], name="frage_reihenfolge_je_test"
            ),
        ]

    def __str__(self) -> str:
        """Gibt den Anfang des Fragetexts zurück."""
        return self.text[:60]


class Antwort(models.Model):
    """Antwortmöglichkeit einer Frage. Pro Frage ist höchstens eine Antwort richtig."""

    frage = models.ForeignKey(Frage, on_delete=models.CASCADE, related_name="antworten")
    text = models.CharField(max_length=500)
    ist_richtig = models.BooleanField(default=False)
    reihenfolge = models.PositiveIntegerField()

    class Meta:
        """Sortierung, höchstens eine richtige Antwort je Frage und Anzeigenamen."""

        ordering = ["reihenfolge"]
        verbose_name = "Antwort"
        verbose_name_plural = "Antworten"
        constraints = [
            models.UniqueConstraint(
                fields=["frage"],
                condition=Q(ist_richtig=True),
                name="hoechstens_eine_richtige_antwort",
            ),
            models.UniqueConstraint(
                fields=["frage", "reihenfolge"], name="antwort_reihenfolge_je_frage"
            ),
        ]

    def __str__(self) -> str:
        """Gibt den Antworttext zurück."""
        return self.text


class Projektaufgabe(models.Model):
    """Kleines Praxisprojekt am Ende einer Phase."""

    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, related_name="projektaufgaben")
    titel = models.CharField(max_length=200)
    beschreibung = models.TextField(help_text="Aufgabenstellung als Markdown.")
    reihenfolge = models.PositiveIntegerField()

    class Meta:
        """Sortierung, Eindeutigkeit innerhalb der Phase und Anzeigenamen."""

        ordering = ["phase", "reihenfolge"]
        verbose_name = "Projektaufgabe"
        verbose_name_plural = "Projektaufgaben"
        constraints = [
            models.UniqueConstraint(
                fields=["phase", "reihenfolge"], name="projektaufgabe_reihenfolge_je_phase"
            ),
        ]

    def __str__(self) -> str:
        """Gibt den Titel zurück."""
        return self.titel


#: Felder von Fortschritt, von denen genau eines gesetzt sein muss.
FORTSCHRITT_ZIELE = ("abschnitt", "quiz", "test", "projektaufgabe")


def _genau_ein_ziel() -> Q:
    """Baut die Bedingung „genau eines der Fortschritts-Ziele ist gesetzt“.

    Returns:
        Eine Q-Bedingung, die genau dann erfüllt ist, wenn von den Feldern in
        FORTSCHRITT_ZIELE genau eines nicht NULL ist.
    """
    bedingung = Q()
    for gesetzt in FORTSCHRITT_ZIELE:
        teil = Q(**{f"{gesetzt}__isnull": False})
        for feld in FORTSCHRITT_ZIELE:
            if feld != gesetzt:
                teil &= Q(**{f"{feld}__isnull": True})
        bedingung |= teil
    return bedingung


class Fortschritt(models.Model):
    """Erledigter Lernschritt eines Nutzers: gelesener Abschnitt, Quiz, Test oder Projekt.

    Genau eines der Ziel-Felder ist gesetzt. Bei Quiz und Test stehen das erreichte
    und das maximale Ergebnis in `punkte` und `max_punkte`.
    """

    nutzer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fortschritte"
    )
    abschnitt = models.ForeignKey(
        Abschnitt, on_delete=models.CASCADE, null=True, blank=True, related_name="fortschritte"
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, null=True, blank=True, related_name="fortschritte"
    )
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, null=True, blank=True, related_name="fortschritte"
    )
    projektaufgabe = models.ForeignKey(
        Projektaufgabe,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="fortschritte",
    )
    punkte = models.PositiveIntegerField(null=True, blank=True)
    max_punkte = models.PositiveIntegerField(null=True, blank=True)
    erledigt_am = models.DateTimeField(auto_now=True)

    class Meta:
        """Genau ein Ziel, ein Eintrag je Nutzer und Ziel, gültige Punkte."""

        ordering = ["-erledigt_am"]
        verbose_name = "Fortschritt"
        verbose_name_plural = "Fortschritte"
        constraints = [
            models.CheckConstraint(condition=_genau_ein_ziel(), name="fortschritt_genau_ein_ziel"),
            models.CheckConstraint(
                condition=(
                    Q(punkte__isnull=True, max_punkte__isnull=True)
                    | Q(
                        punkte__isnull=False,
                        max_punkte__isnull=False,
                        max_punkte__gt=0,
                        punkte__lte=F("max_punkte"),
                    )
                ),
                name="fortschritt_punkte_gueltig",
            ),
            *[
                models.UniqueConstraint(
                    fields=["nutzer", ziel], name=f"fortschritt_einmal_je_{ziel}"
                )
                for ziel in FORTSCHRITT_ZIELE
            ],
        ]

    def __str__(self) -> str:
        """Gibt Nutzer und erledigtes Ziel zurück."""
        ziel = self.abschnitt or self.quiz or self.test or self.projektaufgabe
        return f"{self.nutzer}: {ziel}"
