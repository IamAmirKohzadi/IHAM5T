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

from .api.v1.permissions import RedirectAuthenticatedMixin

from .forms import TemplatedPasswordResetForm


def signup_page(request):
    # Render the signup page unless the user is already authenticated.
    if request.user.is_authenticated:
        return redirect("website:index")
    return render(request, "accounts/signup.html")


def login_page(request, *args, **kwargs):
    # Serve the login view but send authenticated users to home.
    if request.user.is_authenticated:
        return redirect("website:index")
    return LoginView.as_view(template_name="registration/login.html")(request, *args, **kwargs)


@login_required
def profile_page(request):
    # Render the profile page for logged-in users only.
    return render(request, "accounts/profile.html")


# Password reset view using a custom template and redirect-on-auth mixin.
class TemplatedPasswordResetView(RedirectAuthenticatedMixin, PasswordResetView):
    form_class = TemplatedPasswordResetForm
    template_name = "registration/password_reset_form.html"
    success_url = reverse_lazy("password_reset_done")


# Password reset "done" page with auth redirect guard.
class TemplatedPasswordResetDoneView(RedirectAuthenticatedMixin, PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


# Password reset confirmation page with auth redirect guard.
class TemplatedPasswordResetConfirmView(RedirectAuthenticatedMixin, PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"


# Password reset completion page with auth redirect guard.
class TemplatedPasswordResetCompleteView(RedirectAuthenticatedMixin, PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
