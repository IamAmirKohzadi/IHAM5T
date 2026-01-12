from django.contrib import admin
from .models import ContactMessage, SiteSettings, StoryTip, NewsletterSubscriber


# Admin config for site-wide settings.
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["id", "updated_at"]
    fields = ["blog_quote", "ads_image", "ads_link", "ads_description"]


# Admin config for contact form submissions.
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "subject", "status", "created_date"]
    list_filter = ["status", "created_date"]
    search_fields = ["name", "email", "subject"]


# Admin config for story tip submissions.
@admin.register(StoryTip)
class StoryTipAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "contact_email", "status", "created_date"]
    list_filter = ["status", "created_date"]
    search_fields = ["title", "contact_name", "contact_email"]


# Admin config for newsletter subscribers.
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "created_date"]
    search_fields = ["email"]
