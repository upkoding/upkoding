from django.contrib import admin
from django.db import models
from mdeditor.widgets import MDEditorWidget

from account.models import User
from .models import (
    Project,
    ProjectImage,
    UserProject,
    UserProjectEvent,
    UserProjectParticipant
)
from .widgets import ProjectRequirementsWidget


class ProjectImageInlineAdmin(admin.TabularInline):
    model = ProjectImage


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'level', 'status', 'is_premium', 'is_featured', 'codeblock',
                    'taken_count', 'completed_count', 'created',)
    list_display_links = ('title',)
    list_filter = ('status', 'level', 'is_premium', 'is_featured')
    search_fields = ('title', 'user__username',)

    fieldsets = (
        ('Common fields',
         {'fields': ('status',  'level', 'is_featured', 'is_premium', 'user', 'title', 'slug', 'description_short', 'description', 'cover', 'tags',)}),
        ('For Challenge', {
         'fields': ('codeblock',)}),
        ('For Project (legacy)',
         {'fields': ('requirements', 'require_demo_url', 'require_sourcecode_url',)}),
        ('Stats & others',
         {'fields': ('point', 'taken_count', 'completed_count', 'search_vector', )}),
    )
    actions = ['make_copy', ]

    readonly_fields = ('search_vector',)
    formfield_overrides = {
        models.JSONField: {'widget': ProjectRequirementsWidget},
        models.TextField: {'widget': MDEditorWidget},
    }
    inlines = [ProjectImageInlineAdmin]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def make_copy(self, request, queryset):
        if request.user.is_superuser:
            count = 0
            for project in queryset:
                project.copy(request.user)
                count += 1
            self.message_user(
                request, f'{count} project(s) copied.')
    make_copy.short_description = 'Copy projects yang dipilih'


@admin.register(UserProjectEvent)
class UserProjectEventAdmin(admin.ModelAdmin):
    model = UserProjectEvent
    list_display = ('user', 'event_type')


class UserProjectEventAdminInline(admin.TabularInline):
    model = UserProjectEvent


class UserProjectParticipantAdmin(admin.TabularInline):
    model = UserProjectParticipant


@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'user', 'status',
                    'point', 'created', 'updated',)
    list_filter = ('status',)
    list_display_links = ('id', 'project',)
    search_fields = ('project__title', 'user__username',)
    formfield_overrides = {
        models.JSONField: {'widget': ProjectRequirementsWidget},
    }
    inlines = [UserProjectParticipantAdmin, UserProjectEventAdminInline]
