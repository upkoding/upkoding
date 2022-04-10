from django.contrib import admin

from .models import (
    Topic,
    Thread,
    ThreadStat,
    ThreadAnswer,
    ThreadAnswerParticipant,
    ThreadAnswerStat,
    ThreadParticipant,
)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "content_object",
        "thread_count",
        "status",
        "created",
        "updated",
    ]
    list_filter = ["status"]


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "user", "status", "created"]
    list_filter = ["status"]


@admin.register(ThreadStat)
class ThreadStatAdmin(admin.ModelAdmin):
    list_display = ["thread", "type", "value", "created"]
    list_filter = ["type"]


@admin.register(ThreadParticipant)
class ThreadParticipantAdmin(admin.ModelAdmin):
    list_display = ["user", "thread", "subscribed", "created"]


@admin.register(ThreadAnswer)
class ThreadAnswerAdmin(admin.ModelAdmin):
    list_display = ["thread", "user", "parent", "status", "created"]
    list_filter = ["status"]


@admin.register(ThreadAnswerParticipant)
class ThreadAnswerParticipantAdmin(admin.ModelAdmin):
    list_display = ["user", "thread_answer", "subscribed", "created"]


@admin.register(ThreadAnswerStat)
class ThreadAnswerStatAdmin(admin.ModelAdmin):
    list_display = ["thread_answer", "type", "value", "created"]
    list_filter = ["type"]
