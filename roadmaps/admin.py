from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models import Roadmap, RoadmapTopic, RoadmapTopicContent


class RoadmapTopicInlineAdmin(admin.TabularInline):
    model = RoadmapTopic


class RoadmapTopicContentInlineAdmin(admin.TabularInline):
    model = RoadmapTopicContent

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'content_type':
            kwargs['queryset'] = ContentType.objects.filter(model='project')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created',)
    list_display_links = ('title',)
    list_filter = ('status',)

    inlines = [RoadmapTopicInlineAdmin]


@admin.register(RoadmapTopic)
class RoadmapTopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'roadmap', 'status', 'created',)
    list_display_links = ('title',)
    list_filter = ('status', 'roadmap')

    inlines = [RoadmapTopicContentInlineAdmin]
