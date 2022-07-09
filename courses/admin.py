from django.contrib import admin

from .models import (
    Course,
    CourseChapter,
    CourseLesson,
    CourseLessonStatus,
    CourseEnrollment,
)


class CourseChapterInlineAdmin(admin.TabularInline):
    model = CourseChapter


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "user",
        "created",
    )
    list_display_links = ("title",)
    list_filter = ("status",)

    inlines = [CourseChapterInlineAdmin]


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "course",
        "chapter",
        "created",
    )
    list_display_links = ("title",)
    list_filter = ("status",)


@admin.register(CourseLessonStatus)
class CourseLessonStatusAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "lesson",
        "completed",
        "created",
    )
    list_display_links = (
        "user",
        "lesson",
    )
    list_filter = ("completed",)


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "course",
        "created",
    )
    list_display_links = (
        "user",
        "course",
    )
