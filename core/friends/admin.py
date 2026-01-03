from django.contrib import admin

from .models import FriendRequest, Friendship


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "from_profile", "to_profile", "status", "created_date")
    list_filter = ("status", "created_date")
    search_fields = ("from_profile__user__email", "to_profile__user__email")


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("id", "user_a", "user_b", "created_date")
    search_fields = ("user_a__user__email", "user_b__user__email")
