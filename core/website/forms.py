from django import forms

from .models import ContactMessage, StoryTip, NewsletterSubscriber


# Form for contact messages with optional name/email for authenticated users.
class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]

    def __init__(self, *args, **kwargs):
        # Relax name/email requirements for authenticated users.
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and getattr(self.user, "is_authenticated", False):
            self.fields["name"].required = False
            self.fields["email"].required = False


# Form for story tips with optional contact info for authenticated users.
class StoryTipForm(forms.ModelForm):
    class Meta:
        model = StoryTip
        fields = [
            "title",
            "summary",
            "details",
            "location",
            "event_date",
            "source_url",
            "attachment",
            "contact_name",
            "contact_email",
        ]
        widgets = {
            "event_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        # Relax contact fields for authenticated users.
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and getattr(self.user, "is_authenticated", False):
            self.fields["contact_name"].required = False
            self.fields["contact_email"].required = False


# Form for newsletter subscriptions with duplicate protection.
class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]

    def clean_email(self):
        # Enforce case-insensitive uniqueness for subscriptions.
        email = self.cleaned_data["email"].strip().lower()
        if NewsletterSubscriber.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already subscribed.")
        return email
