from django.contrib import admin

from .models import (
    Project,
    ProjectImage,
    UserProject,
    UserProjectEvent,
    UserProjectParticipant
)


class ProjectImageAdmin(admin.TabularInline):
    model = ProjectImage


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    inlines = [ProjectImageAdmin]


class UserProjectEventAdmin(admin.TabularInline):
    model = UserProjectEvent


class UserProjectParticipantAdmin(admin.TabularInline):
    model = UserProjectParticipant


class UserProjectAdmin(admin.ModelAdmin):
    model = UserProject
    inlines = [UserProjectParticipantAdmin, UserProjectEventAdmin]


admin.site.register(Project, ProjectAdmin)
admin.site.register(UserProject, UserProjectAdmin)
