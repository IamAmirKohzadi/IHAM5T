from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from core.recaptcha import verify_recaptcha

from .api.v1.permissions import RedirectAuthenticatedMixin

from .forms import TemplatedPasswordResetForm


# Login view that enforces reCAPTCHA for anonymous users.
class CaptchaLoginView(LoginView):
    template_name = "registration/login.html"

    def post(self, request, *args, **kwargs):
        # Require reCAPTCHA for unauthenticated login attempts.
        if not request.user.is_authenticated:
            token = request.POST.get("g-recaptcha-response")
            is_valid, message = verify_recaptcha(token, request.META.get("REMOTE_ADDR"))
            if not is_valid:
                form = self.get_form()
                form.add_error(None, message)
                return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

def signup_page(request):
    # Render the signup page unless the user is already authenticated.
    if request.user.is_authenticated:
        return redirect("website:index")
    return render(request, "accounts/signup.html")


def login_page(request, *args, **kwargs):
    # Serve the login view but send authenticated users to home.
    if request.user.is_authenticated:
        return redirect("website:index")
    return CaptchaLoginView.as_view()(request, *args, **kwargs)


@login_required
def profile_page(request):
    # Render the profile page for logged-in users only.
    return render(request, "accounts/profile.html")


# Password reset view using a custom template and redirect-on-auth mixin.
class TemplatedPasswordResetView(RedirectAuthenticatedMixin, PasswordResetView):
    form_class = TemplatedPasswordResetForm
    template_name = "registration/password_reset_form.html"
    success_url = reverse_lazy("password_reset_done")

    def post(self, request, *args, **kwargs):
        # Require reCAPTCHA for unauthenticated reset requests.
        if not request.user.is_authenticated:
            token = request.POST.get("g-recaptcha-response")
            is_valid, message = verify_recaptcha(token, request.META.get("REMOTE_ADDR"))
            if not is_valid:
                form = self.get_form()
                form.add_error(None, message)
                return self.form_invalid(form)
        return super().post(request, *args, **kwargs)


# Password reset "done" page with auth redirect guard.
class TemplatedPasswordResetDoneView(RedirectAuthenticatedMixin, PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


# Password reset confirmation page with auth redirect guard.
class TemplatedPasswordResetConfirmView(RedirectAuthenticatedMixin, PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"


# Password reset completion page with auth redirect guard.
class TemplatedPasswordResetCompleteView(RedirectAuthenticatedMixin, PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
