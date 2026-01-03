from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import Profile, User
from friends.api.v1.serializers import FriendRequestSerializer
from friends.models import FriendRequest, Friendship


class TestFriendRequestSerializer(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user_a = User.objects.create_user(
            email="form_a@test.com",
            password="TestPass123!",
        )
        self.user_b = User.objects.create_user(
            email="form_b@test.com",
            password="TestPass123!",
        )
        self.profile_a = Profile.objects.get(user=self.user_a)
        self.profile_b = Profile.objects.get(user=self.user_b)

    def test_reject_self_request(self):
        request = self.factory.post("/")
        request.user = self.user_a
        serializer = FriendRequestSerializer(
            data={"to_profile": self.profile_a.id},
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)

    def test_reject_pending_request(self):
        FriendRequest.objects.create(
            from_profile=self.profile_a,
            to_profile=self.profile_b,
        )
        request = self.factory.post("/")
        request.user = self.user_a
        serializer = FriendRequestSerializer(
            data={"to_profile": self.profile_b.id},
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)

    def test_reject_already_friends(self):
        Friendship.objects.create(user_a=self.profile_a, user_b=self.profile_b)
        request = self.factory.post("/")
        request.user = self.user_a
        serializer = FriendRequestSerializer(
            data={"to_profile": self.profile_b.id},
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
