from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
]
