"""Абстрактные модели — база для всего проекта."""
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("создано", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("изменено", auto_now=True)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """Всё, что видно на сайте: можно скрыть и переставить местами."""

    is_active = models.BooleanField("показывать на сайте", default=True, db_index=True)
    order = models.PositiveIntegerField(
        "порядок", default=100, help_text="Меньше число — выше на странице."
    )

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """Модель ровно с одной записью (настройки сайта)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
