from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User, Profile
from blog.models import Category, Post


class TestPostApiCreate(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="writer@test.com",
            password="Test12345",
            is_verified=True,
        )
        self.profile = Profile.objects.get(user=self.user)
        self.category = Category.objects.create(name="test")
        self.url = reverse("blog:api-v1:post-list")

    def test_verified_user_can_create_post(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "Created via API",
            "content": "Post content",
            "categories": [self.category.name],
            "status": True,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data["status"])
        self.assertTrue(Post.objects.filter(title="Created via API").exists())

    def test_unverified_user_cannot_create_post(self):
        unverified_user = User.objects.create_user(
            email="unverified@test.com",
            password="Test12345",
        )
        self.client.force_authenticate(user=unverified_user)
        payload = {
            "title": "Blocked post",
            "content": "Post content",
            "categories": [self.category.name],
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 403)
