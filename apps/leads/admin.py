from django.contrib import admin
from django.utils.html import format_html

from .models import Lead, QuestionTemplate


@admin.register(QuestionTemplate)
class QuestionTemplateAdmin(admin.ModelAdmin):
    list_display = ("text", "service", "leads_count", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("is_active", "service")
    search_fields = ("text", "hint")

    @admin.display(description="обращений")
    def leads_count(self, obj):
        return obj.leads.count()


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "name",
        "contact_line",
        "question_short",
        "status",
    )
    list_editable = ("status",)
    list_filter = ("status", "contact_method", "created_at")
    search_fields = ("name", "contact", "custom_question", "admin_note")
    date_hierarchy = "created_at"
    list_per_page = 30
    readonly_fields = (
        "created_at",
        "updated_at",
        "question_template",
        "custom_question",
        "name",
        "contact",
        "contact_method",
        "ip_address",
        "user_agent",
        "source_page",
    )
    fieldsets = (
        ("Обращение", {"fields": ("created_at", "question_template", "custom_question")}),
        ("Человек", {"fields": ("name", "contact", "contact_method")}),
        ("Работа с заявкой", {"fields": ("status", "admin_note")}),
        (
            "Техническое",
            {"classes": ("collapse",), "fields": ("ip_address", "user_agent", "source_page", "updated_at")},
        ),
    )
    actions = ["mark_done", "mark_in_progress", "mark_spam"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="контакт")
    def contact_line(self, obj):
        return f"{obj.contact} ({obj.get_contact_method_display()})"

    @admin.display(description="вопрос")
    def question_short(self, obj):
        text = obj.question_text
        short = text if len(text) <= 70 else text[:70] + "…"
        if obj.is_new:
            return format_html("<b>{}</b>", short)
        return short

    @admin.action(description="Отметить как обработанные")
    def mark_done(self, request, queryset):
        updated = queryset.update(status=Lead.Status.DONE)
        self.message_user(request, f"Обработано: {updated}")

    @admin.action(description="Взять в работу")
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=Lead.Status.IN_PROGRESS)
        self.message_user(request, f"В работе: {updated}")

    @admin.action(description="Пометить как спам")
    def mark_spam(self, request, queryset):
        updated = queryset.update(status=Lead.Status.SPAM)
        self.message_user(request, f"Спам: {updated}")
