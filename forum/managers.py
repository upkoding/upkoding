from django.db import models
from django.contrib.contenttypes.models import ContentType


class TopicManager(models.Manager):
    def active(self):
        """
        Returns active answers only.
        Usage:
            `Topic.objects.active()`
        Which is equivalent to:
            `Topic.objects.all(status=1)`
        """
        return self.filter(status=self.model.STATUS_ACTIVE)

    def get_for_project(self, project):
        content_type = ContentType.objects.get_for_model(project.__class__)
        topic = self.get(content_type=content_type, content_id=project.pk)
        return topic

    def get_or_create_for_project(self, project, user=None):
        content_type = ContentType.objects.get_for_model(project.__class__)
        topic, _ = self.get_or_create(
            content_type=content_type,
            content_id=project.pk,
            defaults={
                "title": project.title,
                "description": project.description_short,
                "user": user,
            },
        )
        return topic


class ThreadManager(models.Manager):
    def active(self):
        """
        Returns active threads only.
        Usage:
            `Thread.objects.active()`
        Which is equivalent to:
            `Thread.objects.all(status=1)`
        """
        return self.filter(status=self.model.STATUS_ACTIVE)


class ReplyManager(models.Manager):
    def active(self):
        """
        Returns active replies only.
        Usage:
            `Reply.objects.active()`
        Which is equivalent to:
            `Reply.objects.all(status=1)`
        """
        return self.filter(status=self.model.STATUS_ACTIVE)
