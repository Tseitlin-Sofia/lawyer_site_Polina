from django.views.generic import DetailView, TemplateView

from apps.leads.forms import LeadForm
from apps.leads.models import QuestionTemplate
from apps.services.models import Service, ServiceCategory

from .models import Credential, ExperienceItem


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = (
            ServiceCategory.objects.filter(is_active=True)
            .prefetch_related("services")
            .order_by("order")
        )
        ctx["questions"] = QuestionTemplate.objects.filter(is_active=True).order_by("order")
        ctx["experience"] = ExperienceItem.objects.filter(is_active=True)
        ctx["credentials"] = Credential.objects.filter(is_active=True)
        ctx["form"] = LeadForm()
        return ctx


class ServiceDetailView(DetailView):
    model = Service
    template_name = "services/service_detail.html"
    context_object_name = "service"

    def get_queryset(self):
        return Service.objects.filter(is_active=True).select_related("category")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["questions"] = QuestionTemplate.objects.filter(
            is_active=True, service=self.object
        ).order_by("order")
        ctx["form"] = LeadForm()
        return ctx


class PrivacyView(TemplateView):
    template_name = "core/privacy.html"
