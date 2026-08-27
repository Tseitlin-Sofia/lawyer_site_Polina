"""Общие настройки. Не используются напрямую — только через dev.py / prod.py."""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def env(key: str, default: str = "") -> str:
    """Пустая переменная в .env считается незаданной — иначе она затрёт default."""
    value = os.environ.get(key, "")
    return value if value.strip() else default


def env_bool(key: str, default: bool = False) -> bool:
    return env(key, "1" if default else "0").lower() in ("1", "true", "yes", "on")


def env_list(key: str, default: str = "") -> list[str]:
    raw = env(key, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = env("SECRET_KEY", "dev-insecure-change-me")
DEBUG = False
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "apps.common",
    "apps.core",
    "apps.services",
    "apps.leads",
    "apps.notifications",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- База данных ---------------------------------------------------------
# Пусто -> SQLite в каталоге data/ (его монтируем томом в Docker).
DATA_DIR = Path(env("DATA_DIR", str(BASE_DIR / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Пустая строка в .env — это тоже «не задано». Обычный config() так не считает
# и возвращает пустой словарь, из которого Django собирает заглушку без ENGINE.
DATABASE_URL = env("DATABASE_URL").strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # SQLite задаём словарём, а не URL: путь вида C:\Dev\... в URL не разбирается.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": DATA_DIR / "db.sqlite3",
            "OPTIONS": {"timeout": 20},
        }
    }

# --- Кэш -----------------------------------------------------------------
# Кэш здесь не для скорости, а для счётчика антиспама.
# LocMemCache (по умолчанию) живёт внутри одного процесса: при трёх воркерах
# gunicorn получится три независимых счётчика, и лимит утроится.
# Таблица в базе — общая для всех процессов. Создаётся командой
# python manage.py createcachetable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "site_cache",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Локализация ---------------------------------------------------------
LANGUAGE_CODE = "ru"
TIME_ZONE = env("TIME_ZONE", "Asia/Jerusalem")
USE_I18N = True
USE_TZ = True
LANGUAGES = [("ru", "Русский")]
LOCALE_PATHS = [BASE_DIR / "locale"]

# --- Статика и медиа -----------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Уведомления о заявках ----------------------------------------------
NOTIFICATION_BACKENDS = env_list("NOTIFICATION_BACKENDS", "console")
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")
LEAD_NOTIFY_EMAIL = env("LEAD_NOTIFY_EMAIL")
SITE_URL = env("SITE_URL", "http://localhost:8000").rstrip("/")

EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
# Порт 587 — это TLS, порт 465 — SSL. Одновременно включать нельзя.
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
if EMAIL_USE_SSL:
    EMAIL_USE_TLS = False
# Чтобы зависший SMTP не держал соединение бесконечно.
EMAIL_TIMEOUT = int(env("EMAIL_TIMEOUT", "15"))
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "site@example.com")

# Отправлять уведомления в фоновом потоке, не задерживая ответ клиенту.
NOTIFY_ASYNC = env_bool("NOTIFY_ASYNC", True)

# --- Антиспам ------------------------------------------------------------
LEAD_RATE_LIMIT = int(env("LEAD_RATE_LIMIT", "5") or 5)
LEAD_RATE_WINDOW_MINUTES = int(env("LEAD_RATE_WINDOW_MINUTES", "10") or 10)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
