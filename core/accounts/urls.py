from django.urls import path, include
from accounts.api.v1.views import RegistrationApiView
from . import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("signup/", RegistrationApiView.as_view(), name="signup"),
    path("signup-page/", views.signup_page, name="signup-page"),
    path("profile/", views.profile_page, name="profile-page"),
    path("api/v1/", include("accounts.api.v1.urls")),
]
