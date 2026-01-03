from django.urls import path, include
from accounts.api.v1.views import RegistrationApiView
from . import views

urlpatterns = [
    path("password_reset/", views.TemplatedPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", views.TemplatedPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        views.TemplatedPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("reset/done/", views.TemplatedPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("login/", views.login_page, name="login"),
    path("", include("django.contrib.auth.urls")),
    path("signup/", RegistrationApiView.as_view(), name="signup"),
    path("signup-page/", views.signup_page, name="signup-page"),
    path("profile/", views.profile_page, name="profile-page"),
    path("api/v1/", include("accounts.api.v1.urls")),
]
