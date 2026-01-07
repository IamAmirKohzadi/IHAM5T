from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

from accounts.models import User


class TestAccountApiViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="TestPass123!",
            is_verified=True,
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")# stores emails in memory, which is perfect for tests!
    @patch("accounts.api.v1.views.verify_recaptcha", return_value=(True, ""))
    def test_registration_success(self, *_args):
        url = reverse("registration")
        payload = {
            "email": "new@test.com",
            "password": "TestPass123!",
            "password1": "TestPass123!",
            "g-recaptcha-response": "test-token",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

    def test_activation_confirm_verifies_user(self):
        user = User.objects.create_user(
            email="verify@test.com",
            password="TestPass123!",
        )
        token = str(RefreshToken.for_user(user))
        url = reverse("activation", kwargs={"token": token})
        response = self.client.get(url, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_profile_requires_auth(self):
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_change_password_success(self):
        url = reverse("change-password")
        self.client.force_authenticate(user=self.user)
        payload = {
            "old_password": "TestPass123!",
            "new_password": "NewPass123!",
            "new_password1": "NewPass123!",
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
