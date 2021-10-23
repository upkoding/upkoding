from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import UserProjectEvent
from .notifications import UserProjectEventNotification, delete_activity


@receiver(post_save, sender=UserProjectEvent, dispatch_uid='UserProjectEvent:post_save')
def user_project_event_post_save(sender, instance, created, **kwargs):
    if created:
        # send notification
        UserProjectEventNotification(instance)


@receiver(post_delete, sender=UserProjectEvent, dispatch_uid='UserProjectEvent:post_delete')
def user_project_event_post_delete(sender, instance, using, **kwargs):
    # delete activity
    delete_activity(instance)
