from django.urls import path, include
from rest_framework import routers

from forum.models import Topic, Thread, Reply
from .views import (
    ReplyDetail,
    ReplyList,
    ParticipantDetail,
    ParticipantList,
    TopicList,
    TopicDetail,
    ThreadList,
    ThreadDetail,
    UtilsViewSet,
)

router = routers.SimpleRouter()
router.register("utils", UtilsViewSet, basename="utils")

app_name = "api"

urlpatterns = [
    # topics
    path("topics/", TopicList.as_view(), name="topic_list"),
    path("topics/<int:pk>/", TopicDetail.as_view(), name="topic_detail"),
    path(
        "topics/<int:content_id>/participants/",
        ParticipantList.as_view(content_class=Topic),
        name="topic_participant_list",
    ),
    path(
        "topics/<int:content_id>/participants/<int:pk>/",
        ParticipantDetail.as_view(content_class=Topic),
        name="topic_participant_detail",
    ),
    # threads
    path("threads/", ThreadList.as_view(), name="thread_list"),
    path("threads/<int:pk>/", ThreadDetail.as_view(), name="thread_detail"),
    path(
        "threads/<int:content_id>/participants/",
        ParticipantList.as_view(content_class=Thread),
        name="thread_participant_list",
    ),
    path(
        "threads/<int:content_id>/participants/<int:pk>/",
        ParticipantDetail.as_view(content_class=Thread),
        name="thread_participant_detail",
    ),
    # replies
    path("replies/", ReplyList.as_view(), name="reply_list"),
    path(
        "replies/<int:pk>/",
        ReplyDetail.as_view(),
        name="reply_detail",
    ),
    path(
        "replies/<int:content_id>/participants/",
        ParticipantList.as_view(content_class=Reply),
        name="reply_participant_list",
    ),
    path(
        "replies/<int:content_id>/participants/<int:pk>/",
        ParticipantDetail.as_view(content_class=Reply),
        name="reply_participant_detail",
    ),
    path("", include(router.urls)),
]
