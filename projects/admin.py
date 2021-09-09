from django.contrib import admin
from django.db import models
from mdeditor.widgets import MDEditorWidget

from .models import (
    Project,
    ProjectImage,
    UserProject,
    UserProjectEvent,
    UserProjectParticipant
)
from .widgets import ProjectRequirementsWidget


class ProjectImageAdmin(admin.TabularInline):
    model = ProjectImage


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = ('id', 'title', 'user', 'status', 'is_premium', 'point',
                    'taken_count', 'completed_count', 'created', 'updated',)
    list_display_links = ('id', 'title',)
    search_fields = ('title', 'user__username',)
    readonly_fields = ('search_vector',)
    formfield_overrides = {
        models.JSONField: {'widget': ProjectRequirementsWidget},
        models.TextField: {'widget': MDEditorWidget},
    }
    inlines = [ProjectImageAdmin]


class UserProjectEventAdmin(admin.ModelAdmin):
    model = UserProjectEvent
    list_display = ('user', 'event_type')


class UserProjectEventAdminInline(admin.TabularInline):
    model = UserProjectEvent


class UserProjectParticipantAdmin(admin.TabularInline):
    model = UserProjectParticipant


class UserProjectAdmin(admin.ModelAdmin):
    model = UserProject
    list_display = ('id', 'project', 'user', 'status',
                    'point', 'created', 'updated',)
    list_filter = ('status',)
    list_display_links = ('id', 'project',)
    search_fields = ('project__title', 'user__username',)
    formfield_overrides = {
        models.JSONField: {'widget': ProjectRequirementsWidget},
    }
    inlines = [UserProjectParticipantAdmin, UserProjectEventAdminInline]


admin.site.register(Project, ProjectAdmin)
admin.site.register(UserProject, UserProjectAdmin)
admin.site.register(UserProjectEvent, UserProjectEventAdmin)
