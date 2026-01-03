from django.test import TestCase

from accounts.models import User, Profile


class TestAccountModels(TestCase):
    def test_create_user_sets_active(self):
        user = User.objects.create_user(
            email="active@test.com",
            password="TestPass123!",
        )
        self.assertTrue(user.is_active)

    def test_profile_created_on_user_create(self):
        user = User.objects.create_user(
            email="profile@test.com",
            password="TestPass123!",
        )
        self.assertTrue(Profile.objects.filter(user=user).exists())
