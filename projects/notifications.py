from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import UserProjectEvent, UserProjectParticipant

FROM = settings.DEFAULT_EMAIL_FROM


class UserProjectEventNotification:
    def __init__(self, event: UserProjectEvent):

        self.__user_project = event.user_project
        self.__event_user = event.user
        self.__context = {
            'domain': settings.SITE_DOMAIN,
            'user': self.__event_user,
            'user_project': self.__user_project,
            'project': self.__user_project.project,
        }

        if event.istype(UserProjectEvent.TYPE_REVIEW_MESSAGE):
            self.__notify_project_message()
        if event.istype(UserProjectEvent.TYPE_PROJECT_COMPLETE):
            self.__notify_project_approved()
        if event.istype(UserProjectEvent.TYPE_PROJECT_INCOMPLETE):
            self.__notify_project_disapproved()

    def __notify_project_message(self):
        tpl = 'projects/emails/project_message.html'

        # get all participants on this project, except the event creator.
        participants = UserProjectParticipant.objects. \
            filter(subscribed=True). \
            exclude(user=self.__event_user)
        emails = []
        for p in participants:
            to_user = p.user
            self.__context.update({'to_user': to_user})
            msg = render_to_string(tpl, self.__context)
            emails.append(('[UpKoding] Terdapat pesan dari @{}'.format(self.__event_user.username),
                           msg, FROM, [to_user.email]))
        if emails:
            send_mass_mail(emails, fail_silently=True)

    def __notify_project_approved(self):
        tpl = 'projects/emails/project_approved.html'
        user_project_owner = self.__user_project.user
        self.__context.update({'to_user': user_project_owner})
        msg = render_to_string(tpl, self.__context)
        send_mail('[UpKoding] Proyek kamu telah disetujui!',
                  msg, FROM, [user_project_owner.email], fail_silently=True)

    def __notify_project_disapproved(self):
        tpl = 'projects/emails/project_disapproved.html'
        user_project_owner = self.__user_project.user
        self.__context.update({'to_user': user_project_owner})
        msg = render_to_string(tpl, self.__context)
        send_mail('[UpKoding] Status proyek kamu diralat',
                  msg, FROM, [user_project_owner.email], fail_silently=True)
