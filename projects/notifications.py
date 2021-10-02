from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string

from upkoding.activity_feed import feed_manager
from account.models import User, UserSetting
from .models import UserProjectEvent, UserProjectParticipant

FROM = settings.DEFAULT_EMAIL_FROM


class UserProjectEventNotification:
    def __init__(self, event: UserProjectEvent):
        self.event = event
        self.user_project = event.user_project
        self.project = self.user_project.project
        self.event_user = event.user
        self.context = {
            'domain': settings.SITE_DOMAIN,
            'user': self.event_user,
            'user_project': self.user_project,
            'project': self.project,
        }
        # feed and activity
        self.activity = self.event.create_activity()
        self.user_feed = feed_manager.get_user_feed(self.event_user.pk)
        self.challenge_feed = feed_manager.get_challenge_feed(self.project.pk)
        self.challenge_feed_global = feed_manager.get_global_challenge_feed()

        if event.istype(UserProjectEvent.TYPE_PROJECT_START):
            self._add_to_user_feed()
        if event.istype(UserProjectEvent.TYPE_REVIEW_REQUEST):
            self._notify_review_request()
        if event.istype(UserProjectEvent.TYPE_REVIEW_MESSAGE):
            self._notify_project_message()
        if event.istype(UserProjectEvent.TYPE_PROJECT_COMPLETE):
            self._notify_project_approved()
        if event.istype(UserProjectEvent.TYPE_PROJECT_INCOMPLETE):
            self._notify_project_disapproved()

    def _add_to_user_feed(self):
        """
        Add activity to global, individual challenge feed and user feed.
        """
        notify = [self.challenge_feed, self.challenge_feed_global]
        activity = feed_manager.add_notify_to_activity(self.activity, notify)
        feed_manager.add_activity(self.user_feed, activity=activity)

    def _notify_review_request(self):
        """
        Send email to staff/project creator about project need a review.
        """
        tpl = 'projects/emails/project_review_request.html'

        # get all active staff except event_user
        participants = User.get_active_staffs(exclude_user=self.event_user)

        notify = [self.challenge_feed, self.challenge_feed_global]
        emails = []
        for staff in participants:
            notify.append(feed_manager.get_notification_feed(staff.pk))

            # check user notification settings
            if UserSetting.objects.email_notify_project_review_request(staff):
                self.context.update({'to_user': staff})
                msg = render_to_string(tpl, self.context)
                subject = f'[Proyek] Permintaan review dari @{self.event_user.username}'
                emails.append((subject, msg, FROM, [staff.email]))

        # add to user feed and notify staff
        activity = feed_manager.add_notify_to_activity(self.activity, notify)
        feed_manager.add_activity(self.user_feed, activity)

        # send emails
        if emails:
            send_mass_mail(emails, fail_silently=True)

    def _notify_project_message(self):
        """
        Send email to participants about new message in project.
        """
        tpl = 'projects/emails/project_message.html'

        # get all participants on this project, except the event creator.
        participants = UserProjectParticipant.objects \
            .select_related('user') \
            .filter(user_project=self.user_project, subscribed=True) \
            .exclude(user=self.event_user)

        notify = []
        emails = []
        for p in participants:
            to_user = p.user
            notify.append(feed_manager.get_notification_feed(to_user.pk))

            # check user notification settings
            if UserSetting.objects.email_notify_project_message(to_user):
                self.context.update({'to_user': to_user})
                msg = render_to_string(tpl, self.context)
                subject = f'[Proyek] Pesan dari @{self.event_user.username}'
                emails.append((subject, msg, FROM, [to_user.email]))

        # add to user feed and notify participants
        activity = feed_manager.add_notify_to_activity(self.activity, notify)
        feed_manager.add_activity(self.user_feed, activity)

        if emails:
            send_mass_mail(emails, fail_silently=True)

    def _notify_project_approved(self):
        """
        Send email to user who working on a project about their project has been approved.
        """
        tpl = 'projects/emails/project_approved.html'
        user_project_owner = self.user_project.user

        notify = [self.challenge_feed, self.challenge_feed_global]
        activity = feed_manager.add_notify_to_activity(self.activity, notify)

        if user_project_owner == self.event_user:
            feed_manager.add_activity(self.user_feed, activity)
            return

        # add to approving user and notify user project owner
        activity = feed_manager.add_notify_to_activity(
            activity,
            feed_manager.get_notification_feed(user_project_owner.pk))
        feed_manager.add_activity(self.user_feed, activity)

        # check user notification settings
        if UserSetting.objects.email_notify_project_approved(user_project_owner):
            self.context.update({'to_user': user_project_owner})
            msg = render_to_string(tpl, self.context)
            subject = '[Proyek] Proyek kamu telah disetujui!'
            send_mail(subject, msg, FROM, [
                      user_project_owner.email], fail_silently=True)

    def _notify_project_disapproved(self):
        """
        Send email to user who working on a project about their project status changed.
        """
        tpl = 'projects/emails/project_disapproved.html'
        user_project_owner = self.user_project.user

        # add to disapproving user and notify user project owner
        owner_notification_feed = feed_manager.get_notification_feed(
            user_project_owner.pk)
        activity = feed_manager.add_notify_to_activity(self.activity,
                                                       owner_notification_feed)
        feed_manager.add_activity(self.user_feed, activity)

        # check user notification settings
        if UserSetting.objects.email_notify_project_disapproved(user_project_owner):
            self.context.update({'to_user': user_project_owner})
            msg = render_to_string(tpl, self.context)
            subject = '[Proyek] Status proyek kamu diralat'
            send_mail(subject, msg, FROM, [
                      user_project_owner.email], fail_silently=True)


def delete_activity(instance):
    feed_manager.remove_activity_from_feed(instance)
