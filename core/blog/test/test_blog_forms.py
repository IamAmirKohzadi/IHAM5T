from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User, Profile
from blog.models import Post

class TestCommentApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="commenter@test.com",
            password="Test12345",
            is_verified=True,
        )
        self.profile = Profile.objects.get(user=self.user)
        self.post_public = Post.objects.create(
            author=self.profile,
            title="Public post",
            content="public",
            status=True,
            published_date=datetime.now(),
        )
        self.post_private = Post.objects.create(
            author=self.profile,
            title="Private post",
            content="private",
            status=False,
            published_date=datetime.now(),
        )
        self.url = reverse("blog:api-v1:comment-list")

    def test_create_comment_on_approved_post(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "post": self.post_public.id,
            "message": "Nice post",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["post"], self.post_public.id)

    def test_comment_blocked_for_unapproved_post(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "post": self.post_private.id,
            "message": "Should fail",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
