from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from sorl.thumbnail import ImageField


def roadmap_cover_path(instance, filename):
    ts = int(now().timestamp())
    return 'roadmaps/cover/{}-{}'.format(ts, filename)


class Roadmap(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1

    STATUSES = [
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active'),
    ]

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True)
    description = models.TextField()
    status = models.PositiveSmallIntegerField(
        choices=STATUSES, default=STATUS_INACTIVE)
    cover = ImageField(
        upload_to=roadmap_cover_path,
        blank=True,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug'], name='roadmap_slug_idx'),
            models.Index(fields=['status'], name='roadmap_status_idx'),
        ]

    def __str__(self, *args, **kwargs):
        return self.title

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def get_absolute_url(self):
        return reverse('roadmaps:detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class RoadmapTopic(models.Model):
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1

    STATUSES = [
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active'),
    ]

    roadmap = models.ForeignKey(
        Roadmap, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True)
    description = models.TextField()
    status = models.PositiveSmallIntegerField(
        choices=STATUSES, default=STATUS_INACTIVE)
    order = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug'], name='roadmap_topic_slug_idx'),
            models.Index(fields=['status'], name='roadmap_topic_status_idx'),
            models.Index(fields=['order'], name='roadmap_topic_order_idx'),
        ]
        ordering = ['order']

    def __str__(self, *args, **kwargs):
        return self.title

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class RoadmapTopicContent(models.Model):
    roadmap_topic = models.ForeignKey(
        RoadmapTopic, on_delete=models.CASCADE, related_name='contents')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'content_id')
    order = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['order'],
                         name='roadmap_topic_c_order_idx'),
        ]
        ordering = ['order']

    def __str__(self, *args, **kwargs):
        return f'{self.roadmap_topic} ({self.content_object})'
