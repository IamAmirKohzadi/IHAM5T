from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import Profile
from friends.models import FriendRequest, Friendship
from .serializers import FriendRequestSerializer, FriendshipSerializer


class FriendRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "from_profile", "to_profile"]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return FriendRequest.objects.none()
        if user.is_staff:
            return FriendRequest.objects.all()
        profile = Profile.objects.filter(user=user).first()
        if not profile:
            return FriendRequest.objects.none()
        return FriendRequest.objects.filter(Q(from_profile=profile) | Q(to_profile=profile))

    def perform_create(self, serializer):
        profile = Profile.objects.filter(user=self.request.user).first()
        serializer.save(from_profile=profile)

    def create(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user=request.user).first()
        to_profile_id = request.data.get("to_profile")
        if profile and to_profile_id:
            to_profile = get_object_or_404(Profile, pk=to_profile_id)
            existing = FriendRequest.objects.filter(from_profile=profile, to_profile=to_profile).first()
            if existing and existing.status in (
                FriendRequest.STATUS_DECLINED,
                FriendRequest.STATUS_CANCELED,
            ):
                existing.status = FriendRequest.STATUS_PENDING
                existing.save(update_fields=["status", "updated_date"])
                serializer = self.get_serializer(existing)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def accept(self, request, *args, **kwargs):
        friend_request = self.get_object()
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or friend_request.to_profile_id != profile.id:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if friend_request.status != FriendRequest.STATUS_PENDING:
            return Response({"detail": "Request is not pending."}, status=status.HTTP_400_BAD_REQUEST)
        Friendship.objects.get_or_create(
            user_a=friend_request.from_profile,
            user_b=friend_request.to_profile,
        )
        friend_request.status = FriendRequest.STATUS_ACCEPTED
        friend_request.save(update_fields=["status", "updated_date"])
        serializer = self.get_serializer(friend_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def decline(self, request, *args, **kwargs):
        friend_request = self.get_object()
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or friend_request.to_profile_id != profile.id:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if friend_request.status != FriendRequest.STATUS_PENDING:
            return Response({"detail": "Request is not pending."}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.status = FriendRequest.STATUS_DECLINED
        friend_request.save(update_fields=["status", "updated_date"])
        serializer = self.get_serializer(friend_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, *args, **kwargs):
        friend_request = self.get_object()
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or friend_request.from_profile_id != profile.id:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if friend_request.status != FriendRequest.STATUS_PENDING:
            return Response({"detail": "Request is not pending."}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.status = FriendRequest.STATUS_CANCELED
        friend_request.save(update_fields=["status", "updated_date"])
        serializer = self.get_serializer(friend_request)
        return Response(serializer.data)


class FriendshipViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return Friendship.objects.none()
        if user.is_staff:
            return Friendship.objects.all()
        profile = Profile.objects.filter(user=user).first()
        if not profile:
            return Friendship.objects.none()
        return Friendship.objects.filter(Q(user_a=profile) | Q(user_b=profile))

    @action(detail=True, methods=["post"])
    def remove(self, request, *args, **kwargs):
        friendship = self.get_object()
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or (friendship.user_a_id != profile.id and friendship.user_b_id != profile.id):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
