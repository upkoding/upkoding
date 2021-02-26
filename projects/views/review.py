import json
from django.http.response import HttpResponseForbidden, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from projects.models import UserProject, UserProjectEvent


class ReviewProject(LoginRequiredMixin, DetailView):
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
            user_project.add_event(
                UserProjectEvent.TYPE_REVIEW_MESSAGE,
                user=current_user,
                message=message)
            return JsonResponse({'ok': True})

        # staff can approve projects, but staff project need to be approved by admin :)
        if action == 'approve' and user_project.approvable_by(current_user):
            # TODO: transaction
            user_project.status = UserProject.STATUS_COMPLETE
            user_project.save()

            user_project.add_event(
                UserProjectEvent.TYPE_PROJECT_COMPLETE,
                user=current_user,
                message=message)
            return JsonResponse({'ok': True})

        # only superuser can disapprove (drop the status back to pending review) approved project
        if action == 'disapprove' and current_user.is_superuser:
            # TODO: transaction
            user_project.status = UserProject.STATUS_PENDING_REVIEW
            user_project.save()

            user_project.add_event(
                UserProjectEvent.TYPE_PROJECT_INCOMPLETE,
                user=current_user,
                message=message)
            return JsonResponse({'ok': True})

        return HttpResponseForbidden()
