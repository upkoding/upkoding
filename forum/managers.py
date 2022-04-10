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

    def get_or_create_for_project(self, project):
        content_type = ContentType.objects.get_for_model(project.__class__)
        topic, _ = self.get_or_create(
            content_type=content_type.pk,
            content_id=project.pk,
            defaults={
                "title": project.title,
                "description": project.description_short,
            },
        )
        return topic


class ThreadManager(models.Manager):
    def active(self):
        """
        Returns active answers only.
        Usage:
            `Thread.objects.active()`
        Which is equivalent to:
            `Thread.objects.all(status=1)`
        """
        return self.filter(status=self.model.STATUS_ACTIVE)


class ThreadAnswerManager(models.Manager):
    def active(self):
        """
        Returns active answers only.
        Usage:
            `ThreadAnswer.objects.active()`
        Which is equivalent to:
            `ThreadAnswer.objects.all(status=1)`
        """
        return self.filter(status=self.model.STATUS_ACTIVE)
