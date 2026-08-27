from django.db import models

from apps.common.models import PublishableModel, TimeStampedModel
from apps.services.models import Service


class QuestionTemplate(PublishableModel, TimeStampedModel):
    """Готовая кнопка-вопрос. Человеку не нужно ничего формулировать."""

    text = models.CharField(
        "вопрос",
        max_length=200,
        help_text="Формулировка от лица клиента. Например: «Мне не оплатили сверхурочные».",
    )
    hint = models.CharField(
        "подсказка",
        max_length=200,
        blank=True,
        help_text="Короткое пояснение под вопросом. Необязательно.",
    )
    service = models.ForeignKey(
        Service,
        verbose_name="связанная услуга",
        related_name="question_templates",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "готовый вопрос"
        verbose_name_plural = "Готовые вопросы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class Lead(TimeStampedModel):
    """Обращение с сайта."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Обработана"
        SPAM = "spam", "Спам"

    class ContactMethod(models.TextChoices):
        PHONE = "phone", "Телефон"
        WHATSAPP = "whatsapp", "WhatsApp"
        TELEGRAM = "telegram", "Telegram"
        EMAIL = "email", "Почта"

    name = models.CharField("имя", max_length=120)
    contact = models.CharField("контакт", max_length=150)
    contact_method = models.CharField(
        "способ связи",
        max_length=20,
        choices=ContactMethod.choices,
        default=ContactMethod.PHONE,
    )

    question_template = models.ForeignKey(
        QuestionTemplate,
        verbose_name="выбранный вопрос",
        related_name="leads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    custom_question = models.TextField("свой вопрос", blank=True)

    status = models.CharField(
        "статус", max_length=20, choices=Status.choices, default=Status.NEW, db_index=True
    )
    admin_note = models.TextField("заметка для себя", blank=True)

    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)
    user_agent = models.CharField("браузер", max_length=300, blank=True)
    source_page = models.CharField("страница отправки", max_length=300, blank=True)

    class Meta:
        verbose_name = "заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.question_text[:60]}"

    @property
    def question_text(self):
        if self.question_template:
            return self.question_template.text
        return self.custom_question or "Без вопроса"

    @property
    def is_new(self):
        return self.status == self.Status.NEW
