from .models import SiteSettings


def site_settings(request):
    # Provide site settings to all templates.
    return {"site_settings": SiteSettings.objects.first()}
