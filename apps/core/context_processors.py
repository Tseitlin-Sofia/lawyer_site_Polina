from .models import SiteSettings


def site_settings(request):
    """Настройки сайта доступны в любом шаблоне как {{ site }}."""
    return {"site": SiteSettings.load()}
