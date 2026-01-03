from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Profile, User
from friends.models import FriendRequest


class TestFriendApiViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(
            email="view_a@test.com",
            password="TestPass123!",
        )
        self.user_b = User.objects.create_user(
            email="view_b@test.com",
            password="TestPass123!",
        )
        self.profile_a = Profile.objects.get(user=self.user_a)
        self.profile_b = Profile.objects.get(user=self.user_b)
        self.requests_url = reverse("friends:api-v1:friend-request-list")
        self.friendships_url = reverse("friends:api-v1:friendship-list")

    def test_requests_require_auth(self):
        response = self.client.get(self.requests_url)
        self.assertEqual(response.status_code, 401)

    def test_create_and_accept_friend_request(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.post(
            self.requests_url,
            {"to_profile": self.profile_b.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        request_id = response.data["id"]

        self.client.force_authenticate(user=self.user_b)
        accept_url = reverse(
            "friends:api-v1:friend-request-accept",
            kwargs={"pk": request_id},
        )
        response = self.client.post(accept_url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], FriendRequest.STATUS_ACCEPTED)

        response = self.client.get(self.friendships_url)
        self.assertEqual(response.status_code, 200)
        data = response.data
        items = data.get("results", data) if isinstance(data, dict) else data
        self.assertEqual(len(items), 1)
