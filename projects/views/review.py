import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.generic import DetailView
from django.template.loader import render_to_string

from projects.models import UserProject, UserProjectEvent, UserProjectParticipant


class ProjectReview(LoginRequiredMixin, DetailView):
    model = UserProject

    def post(self, request, *args, **kwargs):
        user_project = self.get_object()

        # payload
        data = json.loads(request.body)
        message = data.get('message', '')
        action = data.get('action', '')

        owner = user_project.user
        current_user = request.user

        # only owner and staff can write message to project timeline
        if action == 'message' and ((current_user == owner) or current_user.is_staff):
            if not message:
                return HttpResponseBadRequest('Pesan tidak boleh kosong!')

            event = user_project.add_event(
                UserProjectEvent.TYPE_REVIEW_MESSAGE,
                user=current_user,
                message=message)

            # add current user as participant if doesn't yet
            UserProjectParticipant.objects.get_or_create(
                user_project=user_project, user=current_user)

            return JsonResponse({
                'message': 'Pesan telah dikirim!',
                'html': render_to_string(f'projects/templatetags/timeline/type_{event.event_type}.html', {
                    'event': event,
                    'event_user': current_user
                })})

        # staff can approve projects, but staff project need to be approved by admin :)
        if action == 'approve' and user_project.approvable_by(current_user):
            with transaction.atomic():
                user_project.set_complete()
                event = user_project.add_event(
                    UserProjectEvent.TYPE_PROJECT_COMPLETE,
                    user=current_user,
                    message=message)

                # add current user as participant if doesn't yet
                UserProjectParticipant.objects.get_or_create(
                    user_project=user_project, user=current_user)

                return JsonResponse({
                    'message': 'Proyek telah disetujui!',
                    'html': render_to_string(f'projects/templatetags/timeline/type_{event.event_type}.html', {
                        'event': event,
                        'event_user': current_user
                    })})

        # only superuser can disapprove (drop the status back to pending review) approved project
        if action == 'disapprove' and current_user.is_superuser:
            if not message:
                return HttpResponseBadRequest('Berikan alasan kenapa proyek ini batal disetujui!')

            was_complete = user_project.is_complete()
            with transaction.atomic():
                user_project.status = UserProject.STATUS_PENDING_REVIEW
                user_project.save()

                # withdraw point and counter if it was approved
                if was_complete:
                    owner.remove_point(user_project.point)

                    # decrement completed count on project
                    project = user_project.project
                    project.dec_completed_count()

                event = user_project.add_event(
                    UserProjectEvent.TYPE_PROJECT_INCOMPLETE,
                    user=current_user,
                    message=message)

                # add current user as participant if doesn't yet
                UserProjectParticipant.objects.get_or_create(
                    user_project=user_project, user=current_user)

                return JsonResponse({
                    'message': 'Proyek batal disetujui!',
                    'html': render_to_string(f'projects/templatetags/timeline/type_{event.event_type}.html', {
                        'event': event,
                        'event_user': current_user
                    })})

        return HttpResponseForbidden('Maaf kamu tidak punya akses melakukan aksi ini.')
