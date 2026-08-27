from django.contrib import admin

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
    list_display = ("title", "issuer", "year", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("title", "issuer")
