"""Локальная разработка."""
from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1"]

# По умолчанию письма НЕ уходят наружу, а печатаются в консоль — так удобно
# отлаживать вёрстку письма, не рассылая ничего.
# Чтобы проверить настоящую отправку через SMTP, добавьте в .env строку:
#   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_BACKEND = env(  # noqa: F405
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

# Manifest-хранилище требует collectstatic — в разработке оно мешает.
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
}
