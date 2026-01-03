from django.urls import include, path


app_name = "friends"

urlpatterns = [
    path("api/v1/", include(("friends.api.v1.urls","api-v1"),namespace="api-v1")),
]
