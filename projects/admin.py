from django.contrib import admin

from .models import Project, UserProject, UserProjectEvent, UserProjectEventParticipant

admin.site.register(Project)
admin.site.register(UserProject)
admin.site.register(UserProjectEvent)
admin.site.register(UserProjectEventParticipant)
