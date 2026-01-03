from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import Profile, User
from friends.models import FriendRequest, Friendship


class TestFriendModels(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="friend_a@test.com",
            password="TestPass123!",
        )
        self.user_b = User.objects.create_user(
            email="friend_b@test.com",
            password="TestPass123!",
        )
        self.profile_a = Profile.objects.get(user=self.user_a)
        self.profile_b = Profile.objects.get(user=self.user_b)

    def test_friend_request_defaults(self):
        request = FriendRequest.objects.create(
            from_profile=self.profile_a,
            to_profile=self.profile_b,
        )
        self.assertEqual(request.status, FriendRequest.STATUS_PENDING)
        self.assertIn(str(self.profile_a.id), str(request))
        self.assertIn(str(self.profile_b.id), str(request))

    def test_friend_request_no_self(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                FriendRequest.objects.create(
                    from_profile=self.profile_a,
                    to_profile=self.profile_a,
                )

    def test_friendship_orders_profiles(self):
        friendship = Friendship.objects.create(
            user_a=self.profile_b,
            user_b=self.profile_a,
        )
        self.assertLess(friendship.user_a_id, friendship.user_b_id)

    def test_friendship_unique_constraint(self):
        Friendship.objects.create(user_a=self.profile_a, user_b=self.profile_b)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Friendship.objects.create(user_a=self.profile_b, user_b=self.profile_a)
