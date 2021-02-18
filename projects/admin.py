from django.contrib import admin

from .models import Project, UserProject

admin.site.register(Project)
admin.site.register(UserProject)
