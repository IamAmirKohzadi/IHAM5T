from rest_framework import permissions
# Allows safe methods and restricts edits to owners or admins.
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permit reads for everyone and writes for owners/admins.
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.author.user == request.user


# Allows safe methods and restricts comment edits to owners.
class IsCommentOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read-only access and enforce comment ownership.
        if request.method in permissions.SAFE_METHODS:
            return True
        if not obj.author:
            return False
        return obj.author.user == request.user


# Allows safe methods and requires verified accounts for writes.
class IsVerifiedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permit reads for everyone but require verified users to write.
        if request.method in permissions.SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "is_verified", False)
