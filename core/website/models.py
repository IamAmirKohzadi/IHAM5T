from django.db import models


class SiteSettings(models.Model):
    blog_quote = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return a stable label for admin displays.
        return "Site Settings"
