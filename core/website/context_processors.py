from django.conf import settings

from .models import SiteSettings


def site_settings(request):
    # Provide site settings and optional map key to all templates.
    google_maps_api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    recaptcha_site_key = getattr(settings, "RECAPTCHA_SITE_KEY", "")
    recaptcha_secret_key = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    secret_key = getattr(settings, "SECRET_KEY", "")
    missing_config_keys = []

    if not google_maps_api_key:
        missing_config_keys.append("GOOGLE_MAPS_API_KEY")
    if not recaptcha_site_key:
        missing_config_keys.append("RECAPTCHA_SITE_KEY")
    if not recaptcha_secret_key:
        missing_config_keys.append("RECAPTCHA_SECRET_KEY")
    if not secret_key or secret_key == "dev-insecure-placeholder":
        missing_config_keys.append("DJANGO_SECRET_KEY")

    return {
        "site_settings": SiteSettings.objects.first(),
        "google_maps_api_key": google_maps_api_key,
        "recaptcha_site_key": recaptcha_site_key,
        "missing_config_keys": missing_config_keys,
    }
