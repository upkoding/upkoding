from django.contrib import admin

from .models import Roadmap, RoadmapTopic, RoadmapTopicContent


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    pass


@admin.register(RoadmapTopic)
class RoadmapTopicAdmin(admin.ModelAdmin):
    pass


@admin.register(RoadmapTopicContent)
class RoadmapTopicContentAdmin(admin.ModelAdmin):
    pass
