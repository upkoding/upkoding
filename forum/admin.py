from django.contrib import admin

from .models import (
    Topic,
    Thread,
    Reply,
    Stat,
    Participant,
)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "content_object",
        "status",
        "created",
        "updated",
    ]
    list_filter = ["status"]


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "topic", "user", "status", "created"]
    list_filter = ["status"]


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "message", "parent", "status", "created"]
    list_filter = ["status"]


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ["id", "content_type", "content_id", "stat_type", "value", "created"]
    list_filter = ["stat_type"]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "content_type", "content_id", "subscribed", "created"]
