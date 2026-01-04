from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

from accounts.models import Profile


# Stores a friend request and its current status.
class FriendRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_DECLINED, "Declined"),
        (STATUS_CANCELED, "Canceled"),
    ]

    from_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
    )
    to_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["from_profile", "to_profile"], name="unique_friend_request"),
            CheckConstraint(
                condition=~Q(from_profile=F("to_profile")), #from_profile must not equal to_profile, so you can’t send a friend request to yourself.
                name="friend_request_no_self",
            ),
        ]

    def __str__(self):
        # Show a compact summary of the request.
        return f"{self.from_profile_id} -> {self.to_profile_id} ({self.status})"


# Represents a mutual friendship between two profiles.
class Friendship(models.Model):
    user_a = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="friendships_initiated",
    )
    user_b = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="friendships_received",
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user_a", "user_b"], name="unique_friendship"),
            CheckConstraint(
                condition=~Q(user_a=F("user_b")),
                name="friendship_no_self",
            ),
        ]

    def save(self, *args, **kwargs):
        # Normalize ordering so (a,b) and (b,a) are treated the same.
        if self.user_a_id and self.user_b_id and self.user_a_id > self.user_b_id:
            self.user_a_id, self.user_b_id = self.user_b_id, self.user_a_id
        super().save(*args, **kwargs)

    def __str__(self):
        # Show the pair of profile IDs for admin readability.
        return f"{self.user_a_id} <-> {self.user_b_id}"
