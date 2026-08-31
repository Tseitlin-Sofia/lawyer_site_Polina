from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.common.models import PublishableModel, TimeStampedModel


class ServiceCategory(PublishableModel, TimeStampedModel):
    title = models.CharField("название направления", max_length=150)
    slug = models.SlugField("адрес в ссылке", max_length=170, unique=True, blank=True)
    description = models.TextField("описание", blank=True)
    is_team_practice = models.BooleanField(
        "веду вместе с коллегами",
        default=False,
        help_text="Отметьте для направлений, которые вы ведёте в команде. "
        "На сайте появится соответствующая пометка.",
    )

    class Meta:
        verbose_name = "направление"
        verbose_name_plural = "Направления"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def active_services(self):
        return self.services.filter(is_active=True)


class Service(PublishableModel, TimeStampedModel):
    class PricePrefix(models.TextChoices):
        NONE = "", "точная цена"
        FROM = "от", "от"
        UPTO = "до", "до"

    category = models.ForeignKey(
        ServiceCategory,
        verbose_name="направление",
        related_name="services",
        on_delete=models.CASCADE,
    )
    title = models.CharField("название услуги", max_length=200)
    slug = models.SlugField("адрес в ссылке", max_length=220, unique=True, blank=True)
    short_description = models.CharField(
        "коротко", max_length=300, blank=True, help_text="Одна строка под названием."
    )
    description = models.TextField("подробное описание", blank=True)

    price = models.DecimalField(
        "цена", max_digits=10, decimal_places=2, null=True, blank=True
    )
    price_prefix = models.CharField(
        "приставка к цене",
        max_length=10,
        choices=PricePrefix.choices,
        blank=True,
        default="",
    )
    price_note = models.CharField(
        "примечание к цене",
        max_length=120,
        blank=True,
        help_text="Например: за консультацию, за час, по договорённости.",
    )
    is_free = models.BooleanField("бесплатно", default=False)

    class Meta:
        verbose_name = "услуга"
        verbose_name_plural = "Услуги"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:service_detail", kwargs={"slug": self.slug})

    @property
    def price_display(self):
        if self.is_free:
            return "Бесплатно"
        if self.price is None:
            return "По договорённости"

        # Валюта берётся из настроек сайта — одна на все услуги.
        # Импорт внутри метода, а не наверху файла: иначе получится
        # круговая зависимость между приложениями services и core.
        from apps.core.models import SiteSettings

        site = SiteSettings.load()
        amount = f"{self.price:,.0f}".replace(",", " ")
        prefix = f"{self.price_prefix} " if self.price_prefix else ""

        if site.currency_before_price:
            return f"{prefix}{site.currency}{amount}".strip()
        return f"{prefix}{amount} {site.currency}".strip()
