# ================================================================
# ФАЙЛ: apps/core/admin.py
# ДЕЙСТВИЕ: заменить файл целиком
# Здесь уже учтён блок «Цены», который вы добавляли для валюты.
# ================================================================
from django.contrib import admin
from django.utils.html import format_html

from apps.common.admin import SingletonAdmin

from .models import Credential, ExperienceItem, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Кто вы", {"fields": ("full_name", "role", "photo")}),
        ("Первый экран", {"fields": ("hero_title", "hero_subtitle", "response_promise")}),
        ("О себе", {"fields": ("about",)}),
        (
            "Контакты",
            {"fields": ("phone", "email", "telegram", "whatsapp", "city", "working_hours")},
        ),
        ("Цены", {"fields": ("currency", "currency_before_price")}),
        (
            "Служебное",
            {
                "classes": ("collapse",),
                "fields": ("meta_description", "privacy_policy"),
            },
        ),
    )


@admin.register(ExperienceItem)
class ExperienceItemAdmin(admin.ModelAdmin):
    list_display = ("period", "title", "organization", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title", "organization", "description")


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "issuer",
        "year",
        "scan_preview",
        "show_scan",
        "is_active",
        "order",
    )
    list_editable = ("show_scan", "is_active", "order")
    list_filter = ("is_active", "show_scan")
    search_fields = ("title", "issuer")
    fields = ("title", "issuer", "year", "scan", "show_scan", "is_active", "order")

    @admin.display(description="скан")
    def scan_preview(self, obj):
        """Маленькое превью в списке — чтобы не открывать каждую запись."""
        if not obj.scan:
            return "—"
        return format_html(
            '<img src="{}" style="height:40px;border:1px solid #ccc;border-radius:2px">',
            obj.scan.url,
        )
