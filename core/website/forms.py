from django import forms

from .models import ContactMessage


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
