from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProjectEvent, UserProjectParticipant
from .notifications import UserProjectEventNotification


@receiver(post_save, sender=UserProjectEvent, dispatch_uid='UserProjectEvent:post_save')
def user_project_event_post_save(sender, instance, created, **kwargs):
    if created:
        # create participant
        UserProjectParticipant.objects.get_or_create(
            user_project=instance.user_project, user=instance.user)
        # send notification
        UserProjectEventNotification(instance)
