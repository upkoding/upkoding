from django.contrib import admin

from .models import Project, UserProject, UserProjectEvent, UserProjectParticipant

admin.site.register(Project)
admin.site.register(UserProject)
admin.site.register(UserProjectEvent)
admin.site.register(UserProjectParticipant)
