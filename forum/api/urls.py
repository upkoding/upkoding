from django.urls import path, include
from rest_framework import routers

from .views import (
    ThreadAnswerDetail,
    ThreadAnswerList,
    ThreadAnswerParticipantDetail,
    ThreadAnswerParticipantList,
    ThreadParticipantDetail,
    ThreadParticipantList,
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
    path("topics/", TopicList.as_view(), name="topic_list"),
    path("topics/<int:pk>/", TopicDetail.as_view(), name="topic_detail"),
    path("threads/", ThreadList.as_view(), name="thread_list"),
    path("threads/<int:pk>/", ThreadDetail.as_view(), name="thread_detail"),
    path(
        "threads/<int:thread_pk>/participants/",
        ThreadParticipantList.as_view(),
        name="thread_participant_list",
    ),
    path(
        "threads/<int:thread_pk>/participants/<int:pk>/",
        ThreadParticipantDetail.as_view(),
        name="thread_participant_detail",
    ),
    path("thread_answers/", ThreadAnswerList.as_view(), name="thread_answer_list"),
    path(
        "thread_answers/<int:pk>/",
        ThreadAnswerDetail.as_view(),
        name="thread_answer_detail",
    ),
    path(
        "thread_answers/<int:thread_answer_pk>/participants/",
        ThreadAnswerParticipantList.as_view(),
        name="thread_answer_participant_list",
    ),
    path(
        "thread_answers/<int:thread_answer_pk>/participants/<int:pk>/",
        ThreadAnswerParticipantDetail.as_view(),
        name="thread_answer_participant_detail",
    ),
    path("", include(router.urls)),
]
