from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("requests/", views.LeadCreateView.as_view(), name="create"),
]
