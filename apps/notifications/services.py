"""Сборка текста уведомления и рассылка по активным каналам."""
import logging
import threading

from django.conf import settings
from django.urls import reverse

from .backends import get_active_backends

logger = logging.getLogger(__name__)


def build_lead_message(lead) -> tuple[str, str, str]:
    subject = f"Новая заявка с сайта: {lead.name}"
    lines = [
        f"Вопрос: {lead.question_text}",
        f"Имя: {lead.name}",
        f"Контакт: {lead.contact} ({lead.get_contact_method_display()})",
        f"Время: {lead.created_at:%d.%m.%Y %H:%M}",
    ]
    if lead.question_template and lead.custom_question:
        lines.insert(1, f"Уточнение: {lead.custom_question}")
    body = "\n".join(lines)

    path = reverse("admin:leads_lead_change", args=[lead.pk])
    url = f"{settings.SITE_URL}{path}"
    return subject, body, url


def dispatch(subject: str, body: str, url: str = "") -> None:
    """Разослать готовое сообщение по всем настроенным каналам."""
    for backend in get_active_backends():
        try:
            backend.send(subject, body, url)
            logger.info("Уведомление отправлено через %s", backend.name)
        except Exception:
            logger.exception("Канал %s не смог отправить уведомление", backend.name)


def notify_new_lead(lead) -> None:
    # Текст собираем сразу: в фоновом потоке лучше не трогать базу.
    subject, body, url = build_lead_message(lead)

    if settings.NOTIFY_ASYNC:
        thread = threading.Thread(
            target=dispatch, args=(subject, body, url), daemon=True
        )
        thread.start()
    else:
        dispatch(subject, body, url)
