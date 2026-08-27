import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import CreateView

from .forms import LeadForm
from .models import Lead

logger = logging.getLogger(__name__)


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def rate_limited(request) -> bool:
    """Не больше N заявок с одного IP за окно."""
    ip = client_ip(request) or "unknown"
    key = f"lead-rate:{ip}"
    count = cache.get(key, 0)
    if count >= settings.LEAD_RATE_LIMIT:
        return True
    cache.set(key, count + 1, settings.LEAD_RATE_WINDOW_MINUTES * 60)
    return False


class LeadCreateView(CreateView):
    model = Lead
    form_class = LeadForm
    http_method_names = ["post"]
    success_message = "Заявка отправлена. Свяжусь с вами в ближайшее время."

    def is_ajax(self):
        return self.request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def post(self, request, *args, **kwargs):
        if rate_limited(request):
            error = "Слишком много заявок подряд. Попробуйте позже или напишите напрямую."
            if self.is_ajax():
                return JsonResponse({"ok": False, "errors": {"__all__": [error]}}, status=429)
            messages.error(request, error)
            return redirect("core:home")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.ip_address = client_ip(self.request)
        lead.user_agent = self.request.META.get("HTTP_USER_AGENT", "")[:300]
        lead.source_page = self.request.META.get("HTTP_REFERER", "")[:300]
        lead.save()
        logger.info("Новая заявка #%s от %s", lead.pk, lead.name)

        if self.is_ajax():
            return JsonResponse({"ok": True, "message": self.success_message})
        messages.success(self.request, self.success_message)
        return redirect("core:home")

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({"ok": False, "errors": form.errors}, status=400)
        messages.error(self.request, "Проверьте заполнение формы.")
        return redirect("core:home")
