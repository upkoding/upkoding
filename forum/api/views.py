from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from upkoding.pagination import NewestIdFirstCursorPagination
from projects.models import Project
from forum.models import (
    Reply,
    Participant,
    Topic,
    Thread,
)
from forum.api.serializers import (
    ReplySerializer,
    TopicSerializer,
    ThreadSerializer,
    ParticipantSerializer,
)

from .permissions import IsOwnerOrReadOnly

# Topic
class TopicList(generics.ListAPIView):
    queryset = Topic.objects.active()
    # we want newly created topic showing first
    serializer_class = TopicSerializer
    pagination_class = NewestIdFirstCursorPagination
    filterset_fields = ["user", "user__username"]


class TopicDetail(generics.RetrieveAPIView):
    queryset = Topic.objects.active()
    serializer_class = TopicSerializer


# Thread
class ThreadList(generics.ListCreateAPIView):
    queryset = Thread.objects.active()
    serializer_class = ThreadSerializer
    # we want newly created thread showing first
    pagination_class = NewestIdFirstCursorPagination
    filterset_fields = ["topic", "user", "user__username"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ThreadDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Thread.objects.active()
    serializer_class = ThreadSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        """Soft delete"""
        instance.status = Thread.STATUS_DELETED
        instance.save()


# Reply
class ReplyList(generics.ListCreateAPIView):
    queryset = Reply.objects.active()
    serializer_class = ReplySerializer
    filterset_fields = ["thread", "user", "user__username", "parent", "level"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReplyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reply.objects.active()
    serializer_class = ReplySerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        """Soft delete"""
        instance.status = Reply.STATUS_DELETED
        instance.save()


# Participant
class ParticipantList(generics.ListCreateAPIView):
    content_class = None
    serializer_class = ParticipantSerializer
    filterset_fields = ["user", "user__username", "subscribed"]

    def get_queryset(self):
        content_id = self.kwargs.get("content_id")
        content_type = self.content_class.get_content_type()
        return Participant.objects.filter(
            content_type=content_type, content_id=content_id
        )

    def perform_create(self, serializer):
        content_id = self.kwargs.get("content_id")
        objects = self.content_class.objects
        if hasattr(objects, "active"):
            content = objects.active().get(pk=content_id)
        else:
            content = objects.get(pk=content_id)
        content_type = self.content_class.get_content_type()
        serializer.save(
            user=self.request.user, content_type=content_type, content_id=content.pk
        )


class ParticipantDetail(generics.RetrieveUpdateAPIView):
    content_class = None
    serializer_class = ParticipantSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        content_type = self.content_class.get_content_type()
        content_id = self.kwargs.get("content_id")
        return Participant.objects.filter(
            content_type=content_type, content_id=content_id
        )


# Utils
class UtilsViewSet(viewsets.ViewSet):
    def err_message(self, msg):
        return {"detail": msg}

    @action(detail=False, methods=["get"], name="Get Topic for a project")
    def get_topic_for_project(self, request):
        project_id = request.query_params.get("project")
        if project_id:
            try:
                project = Project.objects.active().get(pk=project_id)
                topic = Topic.objects.get_for_project(
                    project,
                )
                serializer = TopicSerializer(topic)
                return Response(serializer.data)
            except (ObjectDoesNotExist):
                return Response(
                    self.err_message(f"Topic or Project does not exist"),
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            self.err_message("Missing project in query params"),
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"], name="Create Topic for a project")
    def create_topic_for_project(self, request):
        """
        Return topic for given project_id.
        """
        project_id = request.data.get("project")
        if project_id:
            try:
                project = Project.objects.active().get(pk=project_id)
                topic = Topic.objects.get_or_create_for_project(
                    project, user=request.user
                )
                serializer = TopicSerializer(topic)
                return Response(serializer.data)
            except (ObjectDoesNotExist):
                return Response(
                    self.err_message(f"Topic or Project does not exist"),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            self.err_message("Missing project in body"),
            status=status.HTTP_400_BAD_REQUEST,
        )
