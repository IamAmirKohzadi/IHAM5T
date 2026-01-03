from django.test import TestCase
from django.urls import reverse


class TestFriendApiUrls(TestCase):
    def test_friend_request_list_url(self):
        self.assertEqual(
            reverse("friends:api-v1:friend-request-list"),
            "/friends/api/v1/requests/",
        )

    def test_friend_request_detail_url(self):
        self.assertEqual(
            reverse("friends:api-v1:friend-request-detail", kwargs={"pk": 1}),
            "/friends/api/v1/requests/1/",
        )

    def test_friend_request_accept_url(self):
        self.assertEqual(
            reverse("friends:api-v1:friend-request-accept", kwargs={"pk": 1}),
            "/friends/api/v1/requests/1/accept/",
        )

    def test_friendship_list_url(self):
        self.assertEqual(
            reverse("friends:api-v1:friendship-list"),
            "/friends/api/v1/friendships/",
        )

    def test_friendship_remove_url(self):
        self.assertEqual(
            reverse("friends:api-v1:friendship-remove", kwargs={"pk": 1}),
            "/friends/api/v1/friendships/1/remove/",
        )
