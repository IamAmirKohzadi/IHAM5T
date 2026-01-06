from django.contrib import admin
from .models import ContactMessage, SiteSettings


# Admin config for site-wide settings.
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["id", "updated_at"]


# Admin config for contact form submissions.
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "subject", "status", "created_date"]
    list_filter = ["status", "created_date"]
    search_fields = ["name", "email", "subject"]
