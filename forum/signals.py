from django.db.models.signals import post_save
from django.dispatch import receiver

from .events import OnThreadCreated, OnReplyCreated
from .models import Thread, Reply


@receiver(post_save, sender=Thread, dispatch_uid="Thread:post_save")
def thread_post_save(sender, instance, created, **kwargs):
    if created:
        OnThreadCreated(instance)


@receiver(post_save, sender=Reply, dispatch_uid="Reply:post_save")
def thread_answer_post_save(sender, instance, created, **kwargs):
    if created:
        OnReplyCreated(instance)
