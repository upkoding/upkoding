from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string

from account.models import UserSetting
from .models import Thread, ThreadStat, ThreadParticipant, ThreadAnswer, ThreadAnswerStat, ThreadAnswerParticipant

FROM = settings.DEFAULT_EMAIL_FROM


class OnThreadCreated:
    def __init__(self, thread: Thread):
        self.instance = thread
        self.user = thread.user
        self.topic = thread.topic

        # add creator as thread participant
        self.instance.add_participant(self.user)

        # increment thread_count for instance's topic
        self.topic.inc_thread_count()

        # send notification to Topic subscribers
        self.notify_new_thread()

    def notify_new_thread(self):
        pass


class OnAnswerCreated:
    def __init__(self, answer: ThreadAnswer):
        self.instance = answer
        self.thread = answer.thread
        self.user = answer.user
        self.parent = answer.parent
        self.email_context = {
            'domain': settings.SITE_DOMAIN,
            'user': self.user,
            'thread': self.thread,
            'thread_answer': answer,
            'thread_answer_parent': self.parent,
        }

        if self.parent:
            # thread answer reply: add creator as ThreadAnswerParticipant for its parent answer.
            self.parent.add_participant(self.user)

            # update ThreadAnswerStat
            self.parent.inc_stat(ThreadAnswerStat.TYPE_REPLY_COUNT)

            # send notifications to answer participants
            self.notify_new_reply()
        else:
            # thread answer: add creator as thread participant as well as answer participants
            self.instance.add_participant(self.user)
            self.thread = self.instance.thread
            self.thread.add_participant(self.user)

            # update ThreadStat
            self.thread.inc_stat(ThreadStat.TYPE_ANSWER_COUNT)

            # send notifications to thread participants
            self.notify_new_answer()

    def notify_new_answer(self):
        """Notify all users subscribed to a thread"""
        tpl = 'forum/emails/new_thread_answer.html'
        subscribers = ThreadParticipant.subscribed_to(self.thread, exclude=self.user)
        if subscribers:
            subject = f"[Forum] @{self.user.username} menjawab '{self.thread.title}'"
            msg = render_to_string(tpl, self.email_context)

            # TODO: need better (scalable) solution for this if subscribers number are large.
            emails = []
            for sub in subscribers:
                to_user = sub.user
                if UserSetting.objects.email_notify_forum_activity(to_user):
                    emails.append((subject, msg, FROM, [to_user.email]))

            if emails:
                send_mass_mail(emails, fail_silently=True)

    def notify_new_reply(self):
        """Notify all users subscribed to an answer"""
        tpl = 'forum/emails/new_answer_reply.html'
        subscribers = ThreadAnswerParticipant.subscribed_to(self.parent, exclude=self.user)
        if subscribers:
            msg = render_to_string(tpl, self.email_context)

            # TODO: need better (scalable) solution for this if subscribers number are large.
            emails = []
            for sub in subscribers:
                to_user = sub.user
                jawaban = 'jawabanmu' if self.parent.user_id == to_user.id else 'jawaban'
                subject = f"[Forum] @{self.user.username} membalas {jawaban} di '{self.thread.title}'"

                if UserSetting.objects.email_notify_forum_activity(to_user):
                    emails.append((subject, msg, FROM, [to_user.email]))

            if emails:
                send_mass_mail(emails, fail_silently=True)
