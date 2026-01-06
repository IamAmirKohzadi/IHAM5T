from django.db import models


# Stores site-wide settings managed via the admin.
class SiteSettings(models.Model):
    blog_quote = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return a stable label for admin displays.
        return "Site Settings"


# Stores contact form submissions with admin-only review status.
class ContactMessage(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DECLINED = "declined"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DECLINED, "Declined"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show the subject and sender email for quick admin scanning.
        return f"{self.subject} - {self.email}"
