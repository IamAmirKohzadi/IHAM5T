from rest_framework.routers import DefaultRouter

from .views import FriendRequestViewSet, FriendshipViewSet


app_name = "api-v1"

router = DefaultRouter()
router.register("requests", FriendRequestViewSet, basename="friend-request")
router.register("friendships", FriendshipViewSet, basename="friendship")

urlpatterns = router.urls
