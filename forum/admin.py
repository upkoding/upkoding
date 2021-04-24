from django.contrib import admin

from .models import (
    Topic,
    Thread,
    ThreadStat,
    ThreadAnswer,
    ThreadAnswerParticipant,
    ThreadAnswerStat,
    ThreadParticipant, )


class TopicAdmin(admin.ModelAdmin):
    model = Topic
    list_display = ['title', 'type', 'thread_count', 'status', 'created', 'updated']
    list_filter = ['type', 'status']


class ThreadAdmin(admin.ModelAdmin):
    model = Thread
    list_display = ['title', 'topic', 'user', 'status', 'created']
    list_filter = ['status']


class ThreadStatAdmin(admin.ModelAdmin):
    model = ThreadStat
    list_display = ['thread', 'type', 'value', 'created']
    list_filter = ['type']


class ThreadParticipantAdmin(admin.ModelAdmin):
    model = ThreadParticipant
    list_display = ['user', 'thread', 'subscribed', 'created']


class ThreadAnswerAdmin(admin.ModelAdmin):
    model = ThreadAnswer
    list_display = ['thread', 'user', 'parent', 'status', 'created']
    list_filter = ['status']


class ThreadAnswerParticipantAdmin(admin.ModelAdmin):
    model = ThreadAnswerParticipant
    list_display = ['user', 'thread_answer', 'subscribed', 'created']


class ThreadAnswerStatAdmin(admin.ModelAdmin):
    model = ThreadAnswerStat
    list_display = ['thread_answer', 'type', 'value', 'created']
    list_filter = ['type']


admin.site.register(Topic, TopicAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(ThreadStat, ThreadStatAdmin)
admin.site.register(ThreadParticipant, ThreadParticipantAdmin)
admin.site.register(ThreadAnswer, ThreadAnswerAdmin)
admin.site.register(ThreadAnswerParticipant, ThreadAnswerParticipantAdmin)
admin.site.register(ThreadAnswerStat, ThreadAnswerStatAdmin)
