from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from mail_templated import EmailMessage


# Password reset form that sends emails with a templated body.
class TemplatedPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        # Send a password reset email using the mail_templated backend.
        from_email = from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None) or "admin@admin.com"
        message = EmailMessage("email/password_reset.tpl", context, from_email, to=[to_email])
        message.send()
