from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Thread, ThreadParticipant, ThreadAnswer, ThreadAnswerParticipant


@receiver(post_save, sender=Thread, dispatch_uid='Thread:post_save')
def thread_post_save(sender, instance, created, **kwargs):
    """Set thread participant (to be used for notification)"""
    if created:
        # add creator as thread participant
        ThreadParticipant.objects.create(thread=instance, user=instance.user)
        # TODO: send notification to Topic subscribers


@receiver(post_save, sender=ThreadAnswer, dispatch_uid='ThreadAnswer:post_save')
def thread_answer_post_save(sender, instance, created, **kwargs):
    """Set thread or thread answer participant (to be used for notification)"""
    if created:
        if instance.parent:
            # if thread answer reply: add creator as ThreadAnswerParticipant
            ThreadAnswerParticipant.objects.get_or_create(
                thread_answer=instance.parent, user=instance.user)
            # TODO: send notifications to answer participants
        else:
            # if thread answer: add creator as thread participant as well as answer participants
            ThreadParticipant.objects.get_or_create(
                thread=instance.thread, user=instance.user)
            ThreadAnswerParticipant.objects.get_or_create(
                thread_answer=instance, user=instance.user)
            # TODO: send notifications to thread participants
