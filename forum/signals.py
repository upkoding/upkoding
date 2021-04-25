from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Thread, ThreadStat, ThreadAnswer, ThreadAnswerStat


@receiver(post_save, sender=Thread, dispatch_uid='Thread:post_save')
def thread_post_save(sender, instance, created, **kwargs):
    """Set thread participant (to be used for notification)"""
    if created:
        # add creator as thread participant
        instance.add_participant(instance.user)

        # increment thread_count for instance's topic - TODO: bg-task
        instance.topic.inc_thread_count()

        # TODO: send notification to Topic subscribers


@receiver(post_save, sender=ThreadAnswer, dispatch_uid='ThreadAnswer:post_save')
def thread_answer_post_save(sender, instance, created, **kwargs):
    """Set thread or thread answer participant (to be used for notification)"""
    if created:
        user = instance.user
        parent = instance.parent

        if parent:
            # if thread answer reply: add creator as ThreadAnswerParticipant
            parent.add_participant(user)

            # update ThreadAnswerStat - TODO: bg-task
            parent.inc_stat(ThreadAnswerStat.TYPE_REPLY_COUNT)

            # TODO: send notifications to answer participants
        else:
            thread = instance.thread

            # if thread answer: add creator as thread participant as well as answer participants
            thread.add_participant(user)
            instance.add_participant(user)

            # update ThreadStat - TODO: bg-task
            thread.inc_stat(ThreadStat.TYPE_ANSWER_COUNT)

            # TODO: send notifications to thread participants
