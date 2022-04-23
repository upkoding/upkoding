from django.urls import path, include


app_name = "forum"


urlpatterns = [
    path("api/v1/", include("forum.api.urls", namespace="api")),
]
