from rest_framework import serializers

from account.models import User
from forum.models import (
    Reply,
    Topic,
    Thread,
    Participant,
)


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.URLField(source="avatar_url")
    url = serializers.URLField(source="get_absolute_url")

    class Meta:
        model = User
        fields = ["id", "username", "point", "is_staff", "avatar", "url"]


class TopicSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stats = serializers.DictField(source="get_stats", read_only=True)

    class Meta:
        model = Topic
        fields = [
            "id",
            "user",
            "title",
            "slug",
            "description",
            "image",
            "created",
            "stats",
        ]
        read_only_fields = ["slug", "image"]


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


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = ["id", "user", "subscribed", "created"]

    def create(self, validated_data):
        # make sure there's no duplicate
        participant, _ = Participant.objects.get_or_create(
            user=validated_data.get("user"),
            content_type=validated_data.get("content_type"),
            content_id=validated_data.get("content_id"),
            defaults={"subscribed": validated_data.get("subscribed")},
        )
        return participant


class SubReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = [
            "id",
            "user",
            "thread",
            "message",
            "parent",
            "level",
            "created",
        ]
        read_only_fields = fields


class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stats = serializers.DictField(source="get_stats", read_only=True)
    replies = SubReplySerializer(source="get_replies", many=True, read_only=True)

    class Meta:
        model = Reply
        fields = [
            "id",
            "user",
            "thread",
            "message",
            "parent",
            "level",
            "created",
            "stats",
            "replies",
        ]
        read_only_fields = ["level"]

    def create(self, validated_data):
        # rules:
        # - make sure thread and parent__thread are the same
        # - can not reply to parent that has level=Reply.MAX_LEVEL
        thread = validated_data.get("thread")
        parent = validated_data.get("parent")
        validated_data["level"] = 0

        if parent is not None:
            if thread.id != parent.thread_id:
                raise serializers.ValidationError("parent.thread validation")
            if parent.level >= Reply.MAX_LEVEL:
                raise serializers.ValidationError("reply.level validation error")
            validated_data["level"] = parent.level + 1

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # make sure thread and parent unchanged
        if instance.thread != validated_data.get(
            "thread"
        ) or instance.parent != validated_data.get("parent"):
            raise serializers.ValidationError("thread and parent can not changed")
        return super().update(instance, validated_data)
