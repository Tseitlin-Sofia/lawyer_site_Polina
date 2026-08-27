from django.contrib import admin


class SingletonAdmin(admin.ModelAdmin):
    """Одна запись: без кнопок «добавить» и «удалить»."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
