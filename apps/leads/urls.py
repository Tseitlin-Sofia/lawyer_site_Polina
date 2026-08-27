from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("zayavka/", views.LeadCreateView.as_view(), name="create"),
]
