import copy
from django.http import HttpResponseRedirect
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import transaction

from account.models import User
from projects.models import Project, UserProject, UserProjectEvent
from projects.forms import UserProjectReviewRequestForm


class ProjectList(ListView):
    paginate_by = 12

    def get_queryset(self):
        search_query = self.request.GET.get('s')
        if search_query:
            return Project.objects.search(search_query)
        return Project.objects.active()

    def get_context_data(self, **kwargs):
        search_query = self.request.GET.get('s')
        page = self.request.GET.get('page')

        data = super().get_context_data(**kwargs)
        data['search_query'] = search_query
        # only show featured project on page 1 AND not in search page
        if not search_query and (not page or page == '1'):
            data['featured_projects'] = Project.objects.featured()
        return data


class ProjectDetail(DetailView):
    def get_object(self):
        """
        We need to find object by using `pk` and `slug`.
        """
        user = self.request.user
        obj = get_object_or_404(
            Project,
            pk=self.kwargs.get('pk'),
            slug=self.kwargs.get('slug'),
        )
        # - allow staff to preview inactive project
        # - or if its active
        if user.is_staff or obj.is_active():
            return obj
        raise Http404()

    def get(self, request, *args, **kwargs):
        if request.GET.get('me') == 'true':
            if not request.user.is_authenticated:
                return HttpResponseForbidden()

            project = self.get_object()
            user_project = get_object_or_404(
                UserProject, user=request.user, project=project)
            return JsonResponse({
                'status': user_project.status,
                'color_class': user_project.get_color_class()
            })
        return super().get(request, *args, **kwargs)

    def post(self, request, slug, pk):
        user = request.user
        project = self.get_object()

        next_url = reverse('projects:detail', args=[slug, pk])
        # not authenticated, ask for login
        if not user.is_authenticated:
            messages.warning(
                request,
                'Silahkan login terlebih dahulu sebelum mengerjakan proyek.',
                extra_tags='warning'
            )
            return HttpResponseRedirect(reverse('account:login') + '?next={}'.format(next_url))

        # assign user to the project
        with transaction.atomic():
            user_project, created = project.assign_to(user)
            if created:
                user_project.add_event(UserProjectEvent.TYPE_PROJECT_START)
                messages.info(request,
                              "Selamat mengerjakan `{}`!".format(
                                  project.title),
                              extra_tags='success')
            success_url = reverse('projects:detail_user', args=[
                slug, pk, user.username])
            return HttpResponseRedirect(success_url)


class ProjectDetailUser(DetailView):
    template_name = 'projects/project_detail_user.html'

    def get_object(self):
        """
        We need to find object by using `pk` and `slug`.
        """
        return get_object_or_404(
            Project,
            pk=self.kwargs.get('pk'),
            slug=self.kwargs.get('slug'),
            status=Project.STATUS_ACTIVE
        )

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        user_project = get_object_or_404(
            UserProject, user=user, project=self.object)

        data = super().get_context_data(**kwargs)
        data['user_project'] = user_project

        # show completion form only when:
        # - requirements completed
        # - url has `?form=1`
        # - current user is the owner
        rev_request = self.request.GET.get('form') == '1'
        show_rr_form = user_project.is_requirements_complete() \
            and rev_request \
            and (user == self.request.user)

        if show_rr_form:
            data['rr_form'] = UserProjectReviewRequestForm(
                instance=user_project)
        return data

    def __handle_update(self, request, project, user_project):
        """
        Handle requirements status changes.
        """
        redirect_url = reverse('projects:detail_user', args=[
            project.slug, project.pk, request.user.username])

        # deepcopy to preserve the original state
        requirements = copy.deepcopy(user_project.requirements)
        max_progress = user_project.requirements_completed_percent_max

        if requirements:
            # create a copy and modify this instead so we can compare it later
            requirements_copy = copy.deepcopy(requirements)

            # update requirements_copy
            updated_reqs = map(lambda r: int(r),
                               request.POST.getlist('reqs', []))

            # remove `complete` flag
            for r in requirements_copy:
                if r.get('complete'):
                    del r['complete']

            # assign new flag from `updated_reqs`
            for index in updated_reqs:
                req = requirements_copy[index]
                req['complete'] = True

            # save changes
            user_project.requirements = requirements_copy
            user_project.calculate_progress()
            user_project.save()

            # if all requirements completed, ready for review
            if user_project.is_requirements_complete():
                user_project.add_event(UserProjectEvent.TYPE_PROGRESS_COMPLETE)
                messages.info(request,
                              "Mantap! Proyek kamu siap untuk direview. Klik tombol `Minta Review`",
                              extra_tags='success')
            else:
                _, progress_after, become_complete, _ = UserProject.requirements_diff(
                    requirements, requirements_copy)
                # only create progress update event when progress_after > progress_before
                if progress_after > float(max_progress):
                    for msg in become_complete:
                        user_project.add_event(
                            UserProjectEvent.TYPE_PROGRESS_UPDATE, message=msg)

        return HttpResponseRedirect(redirect_url)

    def __handle_review_request(self, request, project, user_project):
        form = UserProjectReviewRequestForm(
            request.POST, instance=user_project)

        if form.is_valid():
            review_requested = form.submit_review()
            if review_requested:
                user_project.add_event(UserProjectEvent.TYPE_REVIEW_REQUEST)
                messages.info(request,
                              "Great job! Proyek kamu sudah disubmit untuk direview team UpKoding.",
                              extra_tags='success')
            else:
                messages.info(request,
                              "Detail proyek berhasil diupdate!",
                              extra_tags='success')
            return HttpResponse()
        return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json; charset=utf-8')

    def post(self, request, slug, pk, username):
        user = request.user
        request_kind = request.POST.get('kind')
        project_url = reverse('projects:detail', args=[slug, pk])

        # not loggedin?
        if (not user.is_authenticated):
            return HttpResponseRedirect(project_url)

        project = self.get_object()
        user_project = get_object_or_404(
            UserProject, user=user, project=project)

        if request_kind == 'update':
            return self.__handle_update(request, project, user_project)

        if request_kind == 'delete':
            user_project.delete()
            messages.info(request,
                          "Proyek `{}` telah dibatalkan :(".format(
                              project.title),
                          extra_tags='warning')
            return HttpResponse()

        if request_kind == 'review_request':
            return self.__handle_review_request(request, project, user_project)
        return HttpResponseRedirect(project_url)
