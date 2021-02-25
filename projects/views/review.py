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

        owner = user_project.user
        current_user = request.user

        # only owner and staff can write message to project timeline
        if (current_user == owner) or current_user.is_staff:
            user_project.add_event(
                UserProjectEvent.TYPE_REVIEW_MESSAGE,
                user=current_user,
                message=message)
            return JsonResponse({'ok': True})
        return HttpResponseForbidden()


class ApproveProject(LoginRequiredMixin, DetailView):
    model = UserProject

    def post(self, request, *args, **kwargs):
        user_project = self.get_object()

        # payload
        data = json.loads(request.body)
        message = data.get('message', '')

        current_user = request.user

        # staff can approve projects, but staff project need to be approved by admin :)
        if user_project.approvable_by(current_user):
            # TODO: transaction
            user_project.status = UserProject.STATUS_COMPLETE
            user_project.save()

            user_project.add_event(
                UserProjectEvent.TYPE_PROJECT_COMPLETE,
                user=current_user,
                message=message)
            return JsonResponse({'ok': True})

        return HttpResponseForbidden()
