"""Каналы доставки уведомлений.

Чтобы добавить новый канал (SMS, Slack, что угодно) — напишите класс
с методом send() и зарегистрируйте его в BACKENDS. Больше ничего менять не надо.
"""
import logging
from abc import ABC, abstractmethod

import requests
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class NotificationBackend(ABC):
    name = "base"

    @abstractmethod
    def send(self, subject: str, body: str, url: str = "") -> bool: ...

    def is_configured(self) -> bool:
        return True


class ConsoleBackend(NotificationBackend):
    name = "console"

    def send(self, subject, body, url=""):
        logger.info("\n=== %s ===\n%s\n%s\n", subject, body, url)
        return True


class TelegramBackend(NotificationBackend):
    name = "telegram"
    API = "https://api.telegram.org/bot{token}/sendMessage"

    def is_configured(self):
        return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)

    def send(self, subject, body, url=""):
        if not self.is_configured():
            logger.warning("Telegram не настроен: нет токена или chat_id")
            return False
        text = f"<b>{subject}</b>\n\n{body}"
        if url:
            text += f'\n\n<a href="{url}">Открыть в панели</a>'
        response = requests.post(
            self.API.format(token=settings.TELEGRAM_BOT_TOKEN),
            json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        response.raise_for_status()
        return True


class EmailBackend(NotificationBackend):
    name = "email"

    def is_configured(self):
        return bool(settings.LEAD_NOTIFY_EMAIL)

    def send(self, subject, body, url=""):
        if not self.is_configured():
            logger.warning("Почта не настроена: пустой LEAD_NOTIFY_EMAIL")
            return False
        text = body + (f"\n\n{url}" if url else "")
        send_mail(
            subject=subject,
            message=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.LEAD_NOTIFY_EMAIL],
            fail_silently=False,
        )
        return True


BACKENDS = {
    ConsoleBackend.name: ConsoleBackend,
    TelegramBackend.name: TelegramBackend,
    EmailBackend.name: EmailBackend,
}


def get_active_backends() -> list[NotificationBackend]:
    active = []
    for name in settings.NOTIFICATION_BACKENDS:
        backend_cls = BACKENDS.get(name)
        if backend_cls is None:
            logger.warning("Неизвестный канал уведомлений: %s", name)
            continue
        active.append(backend_cls())
    return active
