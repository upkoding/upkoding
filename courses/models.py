from django.db import models
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from sorl.thumbnail import ImageField

from account.models import User


def course_image_path(instance, filename):
    ts = int(now().timestamp())
    return "courses/images/{}-{}".format(ts, filename)


class Course(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1

    STATUSES = [
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True)
    description = models.TextField()
    status = models.PositiveSmallIntegerField(choices=STATUSES, default=STATUS_INACTIVE)
    cover = ImageField(upload_to=course_image_path, blank=True, null=True)
    video_url = models.CharField(max_length=250, blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"], name="course_slug_idx"),
            models.Index(fields=["status"], name="course_status_idx"),
        ]

    def __str__(self, *args, **kwargs):
        return self.title

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CourseChapter(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1

    STATUSES = [
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    ]

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="chapters"
    )
    title = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField(choices=STATUSES, default=STATUS_INACTIVE)
    order = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"], name="course_chapter_status_idx"),
            models.Index(fields=["order"], name="course_chapter_order_idx"),
        ]
        ordering = ["order"]

    def __str__(self, *args, **kwargs):
        return f"{self.course.title} -> {self.title}"


class CourseLesson(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1

    STATUSES = [
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    chapter = models.ForeignKey(
        CourseChapter,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="lessons",
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUSES, default=STATUS_INACTIVE)
    public = models.BooleanField(default=False)
    video_url = models.CharField(max_length=250, blank=True, default="")
    cover = ImageField(upload_to=course_image_path, blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"], name="course_lesson_slug_idx"),
            models.Index(fields=["order"], name="course_lesson_order_idx"),
            models.Index(fields=["status"], name="course_lesson_status_idx"),
        ]
        ordering = ["order"]

    def __str__(self, *args, **kwargs):
        return f"{self.course.title} -> {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "course"], name="user_course_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="unique_user_course"
            )
        ]

    def __str__(self, *args, **kwargs):
        return f"{self.user.username} -> {self.course.title}"


class CourseLessonStatus(models.Model):
    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name="course_lesson_statuses",
    )
    lesson = models.ForeignKey(
        CourseLesson, on_delete=models.CASCADE, related_name="course_lesson_statuses"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="course_lesson_statuses"
    )
    completed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["enrollment", "lesson", "user"],
                name="enrollment_user_lesson_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson", "user"],
                name="unique_enrollment_lesson_status",
            )
        ]

    def __str__(self, *args, **kwargs):
        return f"{self.lesson.title} (complete={self.completed})"
