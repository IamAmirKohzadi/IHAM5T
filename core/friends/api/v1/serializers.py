from rest_framework import serializers
from django.db.models import Q

from accounts.models import Profile
from friends.models import FriendRequest, Friendship


# Serializes friend requests with readable names.
class FriendRequestSerializer(serializers.ModelSerializer):
    from_profile = serializers.PrimaryKeyRelatedField(read_only=True)
    to_profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    from_name = serializers.SerializerMethodField()
    to_name = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = [
            "id",
            "from_profile",
            "to_profile",
            "from_name",
            "to_name",
            "status",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["status", "created_date", "updated_date"]

    def get_from_name(self, obj):
        # Build a display name for the sender.
        profile = obj.from_profile
        if not profile:
            return ""
        full_name = f"{profile.first_name} {profile.last_name}".strip()
        return full_name or profile.user.email

    def get_to_name(self, obj):
        # Build a display name for the recipient.
        profile = obj.to_profile
        if not profile:
            return ""
        full_name = f"{profile.first_name} {profile.last_name}".strip()
        return full_name or profile.user.email

    def validate(self, attrs):
        # Prevent self-requests, duplicates, and requests to friends.
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return attrs
        from_profile = Profile.objects.filter(user=request.user).first()
        to_profile = attrs.get("to_profile")
        if not from_profile or not to_profile:
            return attrs
        if from_profile.id == to_profile.id:
            raise serializers.ValidationError({"detail": "You cannot send a request to yourself."})
        if Friendship.objects.filter(
            Q(user_a=from_profile, user_b=to_profile) | Q(user_a=to_profile, user_b=from_profile)
        ).exists():
            raise serializers.ValidationError({"detail": "You are already friends."})
        if FriendRequest.objects.filter(
            Q(from_profile=from_profile, to_profile=to_profile, status=FriendRequest.STATUS_PENDING)
            | Q(from_profile=to_profile, to_profile=from_profile, status=FriendRequest.STATUS_PENDING)
        ).exists():
            raise serializers.ValidationError({"detail": "A pending request already exists."})
        return attrs


# Serializes friendships from the perspective of the current user.
class FriendshipSerializer(serializers.ModelSerializer):
    friend_id = serializers.SerializerMethodField()
    friend_name = serializers.SerializerMethodField()
    friend_email = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ["id", "user_a", "user_b", "friend_id", "friend_name", "friend_email", "created_date"]
        read_only_fields = fields

    def _get_friend(self, obj):
        # Resolve the "other" profile for the current user.
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None
        profile = Profile.objects.filter(user=request.user).first()
        if not profile:
            return None
        if obj.user_a_id == profile.id:
            return obj.user_b
        if obj.user_b_id == profile.id:
            return obj.user_a
        return None

    def get_friend_id(self, obj):
        # Return the friend's profile ID for this relationship.
        friend = self._get_friend(obj)
        return friend.id if friend else None

    def get_friend_name(self, obj):
        # Return a display name for the friend profile.
        friend = self._get_friend(obj)
        if not friend:
            return ""
        full_name = f"{friend.first_name} {friend.last_name}".strip()
        return full_name or friend.user.email

    def get_friend_email(self, obj):
        # Return the friend's email for display.
        friend = self._get_friend(obj)
        return friend.user.email if friend else ""
