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
    if request.user.is_authenticated:
        return redirect("website:index")
    return render(request, "accounts/signup.html")


def login_page(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect("website:index")
    return LoginView.as_view(template_name="registration/login.html")(request, *args, **kwargs)


@login_required
def profile_page(request):
    return render(request, "accounts/profile.html")


class TemplatedPasswordResetView(RedirectAuthenticatedMixin, PasswordResetView):
    form_class = TemplatedPasswordResetForm
    template_name = "registration/password_reset_form.html"
    success_url = reverse_lazy("password_reset_done")


class TemplatedPasswordResetDoneView(RedirectAuthenticatedMixin, PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class TemplatedPasswordResetConfirmView(RedirectAuthenticatedMixin, PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"


class TemplatedPasswordResetCompleteView(RedirectAuthenticatedMixin, PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
