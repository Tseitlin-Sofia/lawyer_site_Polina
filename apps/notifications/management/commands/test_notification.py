"""Проверка каналов уведомлений без создания настоящей заявки.

    python manage.py test_notification
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.notifications.backends import get_active_backends


class Command(BaseCommand):
    help = "Отправляет тестовое уведомление по всем настроенным каналам"

    def handle(self, *args, **options):
        backends = get_active_backends()
        if not backends:
            self.stderr.write("Ни один канал не включён. Проверьте NOTIFICATION_BACKENDS в .env")
            return

        subject = "Проверка связи"
        body = (
            "Это тестовое сообщение с сайта.\n"
            "Если вы его видите — уведомления о заявках настроены правильно."
        )
        url = f"{settings.SITE_URL}/admin/leads/lead/"

        for backend in backends:
            self.stdout.write(f"→ {backend.name}: ", ending="")
            if not backend.is_configured():
                self.stdout.write(self.style.WARNING("не настроен, пропускаю"))
                continue
            try:
                backend.send(subject, body, url)
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"ошибка — {exc}"))
            else:
                self.stdout.write(self.style.SUCCESS("отправлено"))
