from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string

from account.models import UserSetting
from .models import (
    Thread,
    Reply,
    Participant,
)

FROM = settings.DEFAULT_EMAIL_FROM


class OnThreadCreated:
    def __init__(self, thread: Thread):
        self.instance = thread
        self.user = thread.user
        self.topic = thread.topic
        self.topic_content_object = self.topic.content_object

        # add creator as thread participant
        self.instance.add_participant(self.user)

        # add topic content owner to topic participant
        # so we can notify them about a reply/answer to their thread
        self.topic.add_participant(self.topic_content_object.user)

        # increment thread_count stat for instance's topic
        self.topic.inc_thread_count()

        # send notification to Topic subscribers
        self.email_context = {
            "domain": settings.SITE_DOMAIN,
            "user": self.user,
            "thread": thread,
        }
        self.notify_new_thread()

    def notify_new_thread(self):
        """Notify all users subscribed to a thread"""
        tpl = "forum/emails/new_thread.html"
        subscribers = Participant.subscribed_to(self.topic, exclude_user=self.user)
        if subscribers:
            subject = f"[UpKoding Forum] @{self.user.username} bertanya di '{self.topic_content_object.title}'"
            msg = render_to_string(tpl, self.email_context)

            # TODO: need better (scalable) solution for this if subscribers number are large.
            emails = []
            for sub in subscribers:
                to_user = sub.user
                if UserSetting.objects.email_notify_forum_activity(to_user):
                    emails.append((subject, msg, FROM, [to_user.email]))

            if emails:
                send_mass_mail(emails, fail_silently=True)


class OnReplyCreated:
    def __init__(self, reply: Reply):
        self.instance = reply
        self.thread = reply.thread
        self.user = reply.user
        self.parent = reply.parent
        self.email_context = {
            "domain": settings.SITE_DOMAIN,
            "user": self.user,
            "thread": self.thread,
            "thread_reply": reply,
            "thread_reply_parent": self.parent,
        }

        if self.parent:
            # thread reply's reply: add creator as Participant for its parent reply.
            self.parent.add_participant(self.user)

            # update reply count
            self.parent.inc_reply_count()

            # send notifications to reply participants
            self.notify_new_reply_reply()
        else:
            # thread reply: add creator as thread participant as well as reply participants
            self.instance.add_participant(self.user)
            self.thread = self.instance.thread
            self.thread.add_participant(self.user)

            # update reply count
            self.thread.inc_reply_count()

            # send notifications to thread participants
            self.notify_new_reply()

    def notify_new_reply(self):
        """Notify all users subscribed to a thread"""
        tpl = "forum/emails/new_thread_reply.html"
        subscribers = Participant.subscribed_to(self.thread, exclude_user=self.user)
        if subscribers:
            subject = f"[UpKoding Forum] @{self.user.username} menjawab thread: '{self.thread.title}'"
            msg = render_to_string(tpl, self.email_context)

            # TODO: need better (scalable) solution for this if subscribers number are large.
            emails = []
            for sub in subscribers:
                to_user = sub.user
                if UserSetting.objects.email_notify_forum_activity(to_user):
                    emails.append((subject, msg, FROM, [to_user.email]))

            if emails:
                send_mass_mail(emails, fail_silently=True)

    def notify_new_reply_reply(self):
        """Notify all users subscribed to an reply"""
        tpl = "forum/emails/new_reply_reply.html"
        subscribers = Participant.subscribed_to(self.parent, exclude_user=self.user)
        if subscribers:
            msg = render_to_string(tpl, self.email_context)

            # TODO: need better (scalable) solution for this if subscribers number are large.
            emails = []
            for sub in subscribers:
                to_user = sub.user
                jawaban = (
                    "jawabanmu" if self.parent.user_id == to_user.id else "jawaban"
                )
                subject = f"[UpKoding Forum] @{self.user.username} membalas {jawaban} di thread: '{self.thread.title}'"

                if UserSetting.objects.email_notify_forum_activity(to_user):
                    emails.append((subject, msg, FROM, [to_user.email]))

            if emails:
                send_mass_mail(emails, fail_silently=True)
