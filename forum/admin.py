from django.contrib import admin

from .models import (
    Topic,
    Thread,
    ThreadStat,
    ThreadAnswer,
    ThreadAnswerParticipant,
    ThreadAnswerStat,
    ThreadParticipant,)

admin.site.register(Topic)
admin.site.register(Thread)
admin.site.register(ThreadStat)
admin.site.register(ThreadAnswer)
admin.site.register(ThreadAnswerParticipant)
admin.site.register(ThreadAnswerStat)
admin.site.register(ThreadParticipant)
