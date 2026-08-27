"""Заявка сохранена -> уходит уведомление.

Тонкость: post_save срабатывает внутри транзакции, а не после её фиксации.
Если запрос обёрнут в atomic (а так делает ATOMIC_REQUESTS и любая
вызывающая транзакция), фоновый поток может пойти читать заявку из базы
раньше, чем она там появится, — и не найти её.
transaction.on_commit откладывает вызов до момента, когда данные
действительно записаны. Без транзакции Django выполняет функцию сразу.
"""
import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.services import notify_new_lead

from .models import Lead

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lead)
def send_lead_notification(sender, instance, created, **kwargs):
    if not created:
        return

    def _notify():
        try:
            notify_new_lead(instance)
        except Exception:
            # Заявка уже в базе. Упавшее уведомление не должно ломать ответ клиенту:
            # лучше молча потерять сигнал, чем показать человеку страницу с ошибкой.
            logger.exception("Не удалось отправить уведомление о заявке #%s", instance.pk)

    transaction.on_commit(_notify)
