"""Django-Einstellungen der Lern-App.

Alle umgebungsabhängigen Werte kommen aus Umgebungsvariablen. Für die lokale
Entwicklung werden sie zusätzlich aus `backend/.env` geladen (siehe
`.env.example`). Echte Zugangsdaten stehen nie im Code.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

from config.env import env_bool, env_date, env_list, env_required

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = env_required("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1")
# Render setzt den öffentlichen Hostnamen des Dienstes selbst (siehe docs/DEPLOYMENT.md).
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if _render_host:
    ALLOWED_HOSTS.append(_render_host)

# Adressen des Frontends, die die API aufrufen dürfen (CORS). Lokal leer: Der Vite-Proxy genügt.
CORS_ALLOWED_ORIGINS = env_list("DJANGO_CORS_ORIGINS", default="")

# Im Betrieb hinter dem Render-Proxy: HTTPS erzwingen und Cookies absichern.
# Lokal und in Tests aus, weil dort kein HTTPS läuft.
if env_bool("DJANGO_HTTPS_ERZWINGEN", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    # Der Health-Check der Plattform läuft ohne Umleitung.
    SECURE_REDIRECT_EXEMPT = [r"^api/health/$"]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "core",
    "lernen",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        env_required("DATABASE_URL"), conn_max_age=600, conn_health_checks=True
    ),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Erster Tag des Wochenplans (Montag, 16.11.2026). Davor zeigt der Plan keine Abschnitte.
LERNSTART = env_date("LERNTOOL_LERNSTART", "2026-11-16")

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # Zugang per Token (siehe docs/ENTSCHEIDUNGEN.md, B2). Ohne Anmeldung nur /api/health/.
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # Bremst das Durchprobieren von Passwörtern am Login.
    "DEFAULT_THROTTLE_RATES": {"login": "10/min"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
