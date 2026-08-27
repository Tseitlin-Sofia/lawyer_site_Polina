from django.contrib import admin

from .models import Service, ServiceCategory


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ("title", "price_prefix", "price", "price_note", "is_free", "order", "is_active")
    prepopulated_fields = {}


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "is_team_practice", "is_active", "order")
    list_editable = ("is_team_practice", "is_active", "order")
    list_filter = ("is_active", "is_team_practice")
    search_fields = ("title", "description")
    inlines = [ServiceInline]
    exclude = ("slug",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price_display", "is_active", "order")
    list_editable = ("is_active", "order")
    list_filter = ("category", "is_active", "is_free")
    search_fields = ("title", "short_description", "description")
    exclude = ("slug",)
    fieldsets = (
        (None, {"fields": ("category", "title", "short_description", "description")}),
        (
            "Цена",
            {"fields": ("is_free", "price_prefix", "price", "currency", "price_note")},
        ),
        ("Показ на сайте", {"fields": ("is_active", "order")}),
    )

    @admin.display(description="цена")
    def price_display(self, obj):
        return obj.price_display
