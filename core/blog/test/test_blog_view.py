from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User, Profile
from blog.models import Post, Category


class TestBlogApiViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            password="Test12345",
            is_verified=True,
        )
        self.profile = Profile.objects.get(user=self.user)
        self.category = Category.objects.create(name="test")
        self.post_public = Post.objects.create(
            author=self.profile,
            title="Public post",
            content="public",
            status=True,
            published_date=datetime.now(),
        )
        self.post_public.categories.add(self.category)
        self.post_private = Post.objects.create(
            author=self.profile,
            title="Private post",
            content="private",
            status=False,
            published_date=datetime.now(),
        )
        self.post_private.categories.add(self.category)

    def test_post_list_anonymous_filters_unapproved(self):
        url = reverse("blog:api-v1:post-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.post_public.id)

    def test_post_list_owner_can_include_unapproved(self):
        url = reverse("blog:api-v1:post-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            url,
            {
                "author": self.profile.id,
                "include_unapproved": "1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_post_detail_unapproved_is_hidden(self):
        url = reverse("blog:api-v1:post-detail", kwargs={"pk": self.post_private.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
