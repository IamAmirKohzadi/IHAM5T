from django.test import TestCase
from django.urls import reverse


class TestAccountApiUrls(TestCase):
    def test_registration_url(self):
        self.assertEqual(reverse("registration"), "/accounts/api/v1/registration/")

    def test_activation_confirm_url(self):
        self.assertEqual(
            reverse("activation", kwargs={"token": "sample-token"}),
            "/accounts/api/v1/activation/confirm/sample-token",
        )

    def test_profile_url(self):
        self.assertEqual(reverse("profile"), "/accounts/api/v1/profile/")

    def test_change_password_url(self):
        self.assertEqual(reverse("change-password"), "/accounts/api/v1/profile/change-password/")

    def test_jwt_refresh_url(self):
        self.assertEqual(reverse("jwt-refresh"), "/accounts/api/v1/jwt/refresh/")

    def test_jwt_verify_url(self):
        self.assertEqual(reverse("jwt-verify"), "/accounts/api/v1/jwt/verify/")
