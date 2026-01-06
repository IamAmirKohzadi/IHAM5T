from django.conf import settings

from .models import SiteSettings


def site_settings(request):
    # Provide site settings and optional map key to all templates.
    return {
        "site_settings": SiteSettings.objects.first(),
        "google_maps_api_key": getattr(settings, "GOOGLE_MAPS_API_KEY", ""),
        "recaptcha_site_key": getattr(settings, "RECAPTCHA_SITE_KEY", ""),
    }
