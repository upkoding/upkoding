from rest_framework import serializers

from account.models import User
from forum.models import (
    ThreadAnswer,
    ThreadAnswerParticipant,
    Topic,
    Thread,
    ThreadParticipant,
)


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.URLField(source="avatar_url")
    url = serializers.URLField(source="get_absolute_url")

    class Meta:
        model = User
        fields = ["id", "username", "point", "is_staff", "avatar", "url"]


class TopicSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Topic
        fields = [
            "id",
            "user",
            "title",
            "slug",
            "description",
            "image",
            "thread_count",
            "created",
        ]
        read_only_fields = ["slug", "image", "thread_count"]


class ThreadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stats = serializers.DictField(source="get_stats", read_only=True)

    class Meta:
        model = Thread
        fields = [
            "id",
            "user",
            "title",
            "slug",
            "topic",
            "description",
            "created",
            "stats",
        ]
        read_only_fields = ["slug"]


class ThreadParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ThreadParticipant
        fields = ["id", "user", "subscribed", "created"]

    def create(self, validated_data):
        # make sure there's no duplicate
        participant, _ = ThreadParticipant.objects.get_or_create(
            user=validated_data.get("user"),
            thread=validated_data.get("thread"),
            defaults={"subscribed": validated_data.get("subscribed")},
        )
        return participant


class ThreadAnswerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stats = serializers.DictField(source="get_stats", read_only=True)

    class Meta:
        model = ThreadAnswer
        fields = ["id", "user", "thread", "message", "parent", "created", "stats"]

    def create(self, validated_data):
        # make sure thread and parent__thread are the same
        thread = validated_data.get("thread")
        parent = validated_data.get("parent")
        if parent is not None and thread.id != parent.thread_id:
            raise serializers.ValidationError("parent must be in the same thread")

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # make sure thread and parent unchanged
        if instance.thread != validated_data.get(
            "thread"
        ) or instance.parent != validated_data.get("parent"):
            raise serializers.ValidationError("thread and parent can not changed")
        return super().update(instance, validated_data)


class ThreadAnswerParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ThreadAnswerParticipant
        fields = ["id", "user", "subscribed", "created"]

    def create(self, validated_data):
        # make sure there's no duplicate
        participant, _ = ThreadAnswerParticipant.objects.get_or_create(
            user=validated_data.get("user"),
            thread_answer=validated_data.get("thread_answer"),
            defaults={"subscribed": validated_data.get("subscribed")},
        )
        return participant
