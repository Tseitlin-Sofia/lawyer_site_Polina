from django.db import models

from apps.common.models import PublishableModel, SingletonModel, TimeStampedModel


class SiteSettings(SingletonModel, TimeStampedModel):
    """Всё, что меняется в шапке, подвале и блоке «обо мне»."""

    full_name = models.CharField(
        "имя и фамилия",
        max_length=150,
        default="Имя Фамилия"
    )
    role = models.CharField(
        "кто вы", max_length=150, default="Юрист по трудовому праву"
    )
    hero_title = models.CharField(
        "заголовок на первом экране",
        max_length=200,
        default="Разберёмся, что происходит на вашей работе",
    )
    hero_subtitle = models.TextField(
        "подзаголовок на первом экране",
        blank=True,
        default="Выберите вопрос, который ближе всего к вашей ситуации. "
        "Формулировать ничего не нужно — я перезвоню и уточню детали сама.",
    )
    about = models.TextField(
        "о себе",
        blank=True,
        help_text="Обычный текст. Пустая строка разделяет абзацы.",
    )
    photo = models.ImageField("фотография", upload_to="site/", blank=True)

    phone = models.CharField("телефон", max_length=50, blank=True)
    email = models.EmailField("почта", blank=True)
    telegram = models.CharField(
        "Telegram", max_length=100, blank=True, help_text="Без @, например: anna_law"
    )
    whatsapp = models.CharField(
        "WhatsApp", max_length=50, blank=True, help_text="Только цифры, например: 972501234567"
    )
    city = models.CharField("город", max_length=100, blank=True)
    working_hours = models.CharField("часы приёма", max_length=150, blank=True)

    response_promise = models.CharField(
        "обещание по времени ответа",
        max_length=150,
        blank=True,
        default="Отвечаю в течение рабочего дня",
    )

    meta_description = models.CharField(
        "описание для поисковиков", max_length=300, blank=True
    )
    privacy_policy = models.TextField(
        "текст политики обработки данных",
        blank=True,
        help_text="Показывается на отдельной странице, ссылка есть в форме заявки.",
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    @property
    def whatsapp_link(self):
        return f"https://wa.me/{self.whatsapp}" if self.whatsapp else ""

    @property
    def telegram_link(self):
        return f"https://t.me/{self.telegram}" if self.telegram else ""

    @property
    def about_paragraphs(self):
        return [p.strip() for p in self.about.split("\n\n") if p.strip()]


class ExperienceItem(PublishableModel, TimeStampedModel):
    """Запись в блоке опыта — по образцу трудовой книжки."""

    period = models.CharField(
        "период", max_length=50, help_text="Например: 2019 — сейчас"
    )
    title = models.CharField("должность или роль", max_length=200)
    organization = models.CharField("место", max_length=200, blank=True)
    description = models.TextField("что делала", blank=True)

    class Meta:
        verbose_name = "запись об опыте"
        verbose_name_plural = "Опыт работы"
        ordering = ["order", "-id"]

    def __str__(self):
        return f"{self.period} — {self.title}"


class Credential(PublishableModel, TimeStampedModel):
    """Образование, лицензии, курсы."""

    title = models.CharField("название", max_length=200)
    issuer = models.CharField("кем выдано", max_length=200, blank=True)
    year = models.CharField("год", max_length=20, blank=True)

    class Meta:
        verbose_name = "образование и допуски"
        verbose_name_plural = "Образование и допуски"
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title
