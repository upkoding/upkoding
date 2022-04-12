from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from projects.models import Project
from forum.models import (
    ThreadAnswer,
    ThreadAnswerParticipant,
    ThreadParticipant,
    Topic,
    Thread,
)
from forum.api.serializers import (
    ThreadAnswerParticipantSerializer,
    ThreadAnswerSerializer,
    ThreadParticipantSerializer,
    TopicSerializer,
    ThreadSerializer,
)

from .permissions import IsOwnerOrReadOnly

# Topic
class TopicList(generics.ListAPIView):
    queryset = Topic.objects.active()
    serializer_class = TopicSerializer
    filterset_fields = ["user", "user__username"]


class TopicDetail(generics.RetrieveAPIView):
    queryset = Topic.objects.active()
    serializer_class = TopicSerializer


# Thread
class ThreadList(generics.ListCreateAPIView):
    queryset = Thread.objects.active()
    serializer_class = ThreadSerializer
    filterset_fields = ["topic", "user", "user__username"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ThreadDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Thread.objects.active()
    serializer_class = ThreadSerializer
    permission_classes = [IsOwnerOrReadOnly]


# Thread Participant
class ThreadParticipantList(generics.ListCreateAPIView):

    serializer_class = ThreadParticipantSerializer
    filterset_fields = ["user", "user__username", "subscribed"]

    def get_queryset(self):
        thread_id = self.kwargs.get("thread_pk")
        return ThreadParticipant.objects.filter(thread=thread_id)

    def perform_create(self, serializer):
        thread_id = self.kwargs.get("thread_pk")
        thread = Thread.objects.active().get(pk=thread_id)
        serializer.save(user=self.request.user, thread=thread)


class ThreadParticipantDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ThreadParticipantSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        thread_id = self.kwargs.get("thread_pk")
        return ThreadParticipant.objects.filter(thread=thread_id)


# ThreadAnswer
class ThreadAnswerList(generics.ListCreateAPIView):
    queryset = ThreadAnswer.objects.active()
    serializer_class = ThreadAnswerSerializer
    filterset_fields = ["thread", "user", "user__username", "parent"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ThreadAnswerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ThreadAnswer.objects.active()
    serializer_class = ThreadAnswerSerializer
    permission_classes = [IsOwnerOrReadOnly]


# Thread Answer Participant
class ThreadAnswerParticipantList(generics.ListCreateAPIView):

    serializer_class = ThreadAnswerParticipantSerializer
    filterset_fields = ["user", "user__username", "subscribed"]

    def get_queryset(self):
        thread_answer_id = self.kwargs.get("thread_answer_pk")
        return ThreadAnswerParticipant.objects.filter(thread_answer=thread_answer_id)

    def perform_create(self, serializer):
        thread_answer_id = self.kwargs.get("thread_answer_pk")
        thread_answer = ThreadAnswer.objects.active().get(pk=thread_answer_id)
        serializer.save(user=self.request.user, thread_answer=thread_answer)


class ThreadAnswerParticipantDetail(generics.RetrieveUpdateAPIView):
    serializer_class = ThreadAnswerParticipantSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        thread_answer_id = self.kwargs.get("thread_answer_pk")
        return ThreadAnswerParticipant.objects.filter(thread_answer=thread_answer_id)


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
