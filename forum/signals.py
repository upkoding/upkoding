from django.db.models.signals import post_save
from django.dispatch import receiver

from .events import OnThreadCreated, OnAnswerCreated
from .models import Thread, ThreadAnswer


@receiver(post_save, sender=Thread, dispatch_uid='Thread:post_save')
def thread_post_save(sender, instance, created, **kwargs):
    if created:
        OnThreadCreated(instance)


@receiver(post_save, sender=ThreadAnswer, dispatch_uid='ThreadAnswer:post_save')
def thread_answer_post_save(sender, instance, created, **kwargs):
    if created:
        OnAnswerCreated(instance)
