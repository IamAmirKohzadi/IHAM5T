from django.db import models


# Stores site-wide settings managed via the admin.
class SiteSettings(models.Model):
    blog_quote = models.TextField(blank=True)
    ads_image = models.ImageField(upload_to="ads/", blank=True, null=True)
    ads_link = models.URLField(blank=True)
    ads_description = models.TextField(blank=True)
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


# Stores newsletter subscribers for admin review.
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Display the subscriber email in admin lists.
        return self.email


# Stores story tips submitted by users for editorial review.
class StoryTip(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DECLINED = "declined"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DECLINED, "Declined"),
    ]

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    details = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    event_date = models.DateTimeField(blank=True, null=True)
    source_url = models.URLField(blank=True)
    attachment = models.FileField(upload_to="story_tips/", blank=True, null=True)
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show the title and contact email for admin scanning.
        return f"{self.title} - {self.contact_email}"
