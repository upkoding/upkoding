import copy
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import ListView, DetailView
from stream_django.enrich import Enrich
from upkoding.activity_feed import feed_manager

from account.models import User
from projects.forms import UserProjectReviewRequestForm, UserProjectCodeSubmissionForm
from projects.models import Project, UserProject, UserProjectEvent

log = logging.getLogger(__file__)


class ProjectList(ListView):
    paginate_by = 15

    def get_queryset(self):
        search_query = self.request.GET.get('s')
        if search_query:
            if search_query == 'level:easy':
                return Project.objects.active().filter(level=Project.LEVEL_EASY)
            elif search_query == 'level:medium':
                return Project.objects.active().filter(level=Project.LEVEL_MEDIUM)
            elif search_query == 'level:hard':
                return Project.objects.active().filter(level=Project.LEVEL_HARD)
            elif search_query == 'level:project':
                return Project.objects.active().filter(level=Project.LEVEL_PROJECT).order_by('status')
            elif search_query == 'pricing:pro':
                return Project.objects.active().filter(is_premium=True)
            else:
                return Project.objects.search(search_query)
        return Project.objects.active().order_by('level')

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
        if user.is_staff or obj.is_active() or obj.is_archived():
            return obj
        raise Http404()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        project = data.get('object')

        user = self.request.user
        data['project_owner'] = project.user

        if project.is_archived():
            messages.warning(
                self.request,
                'Maaf tantangan ini sudah diarsip, tidak bisa dikerjakan.',
                extra_tags='warning'
            )

        if user.is_authenticated:
            try:
                data['my_project'] = UserProject.objects.get(
                    project=project,
                    user=user
                )
            except UserProject.DoesNotExist:
                pass

        user_projects = UserProject.objects \
            .select_related('user') \
            .filter(
                project=project,
                status__in=(UserProject.STATUS_IN_PROGRESS,
                            UserProject.STATUS_COMPLETE,
                            UserProject.STATUS_PENDING_REVIEW)
            ).order_by('-created')[:10]
        data['user_projects'] = user_projects

        # activity
        try:
            enricher = Enrich(('actor', 'target',))
            feed = feed_manager.get_challenge_feed(challenge_id=project.pk)
            activities = feed.get(limit=6)['results']
            data['activities'] = enricher.enrich_activities(activities)
        except Exception as e:
            log.error(e)

        return data

    def post(self, request, slug, pk):
        user = request.user
        project = self.get_object()

        next_url = reverse('projects:detail', args=[slug, pk])

        # if archived, redirect to project detail
        if project.is_archived():
            return HttpResponseRedirect(next_url)

        # not authenticated, ask for login
        if not user.is_authenticated:
            messages.warning(
                request,
                'Silahkan login terlebih dahulu sebelum mengerjakan tantangan.',
                extra_tags='warning'
            )
            return HttpResponseRedirect(reverse('account:login') + '?next={}'.format(next_url))

        # premium challenge and not a pro user? redirect to pro page
        if project.is_premium and not user.is_pro_user():
            return HttpResponseRedirect(reverse('base:pro'))

        # assign user to the project
        with transaction.atomic():
            user_project, created = project.assign_to(user)
            if created:
                user_project.add_event(UserProjectEvent.TYPE_PROJECT_START)
                messages.info(request,
                              f"Selamat mengerjakan '{project.title}'!",
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
            status__in=[Project.STATUS_ACTIVE, Project.STATUS_ARCHIVED]
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        project = data.get('object')
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        user_project = get_object_or_404(
            UserProject,
            user=user,
            project=self.object
        )

        data['project_owner'] = project.user
        data['user_project'] = user_project
        data['user_project_owner'] = user

        user_projects = UserProject.objects \
            .select_related('user') \
            .filter(project=project,
                    status__in=(UserProject.STATUS_IN_PROGRESS,
                                UserProject.STATUS_COMPLETE,
                                UserProject.STATUS_PENDING_REVIEW)) \
            .order_by('-created')[:10]
        data['user_projects'] = user_projects

        # activity
        try:
            enricher = Enrich(('actor', 'target',))
            feed = feed_manager.get_challenge_feed(challenge_id=project.pk)
            activities = feed.get(limit=6)['results']
            data['activities'] = enricher.enrich_activities(activities)
        except Exception as e:
            log.error(e)

        # show completion form only when:
        # - requirements completed
        # - current user is the owner
        show_review_request_form = user_project.is_requirements_complete() \
            and (user == self.request.user)
        if show_review_request_form:
            data['review_request_form'] = UserProjectReviewRequestForm(
                instance=user_project
            )
        return data

    def _handle_code_submission(self, project, user_project):
        request = self.request
        user = request.user

        submission = UserProjectCodeSubmissionForm(
            user, project, user_project, request.POST
        )
        if submission.is_valid():
            codeblock = submission.run()
            data = {
                'result': codeblock.run_result_summary(),
                'completed': False
            }

            if (codeblock.is_expecting_output and codeblock.is_output_match) or (not codeblock.is_expecting_output and codeblock.is_run_accepted):
                with transaction.atomic():
                    user_project.set_complete()
                    user_project.add_event(
                        UserProjectEvent.TYPE_PROJECT_COMPLETE,
                        user=user)
                    data['completed'] = True

            return JsonResponse(data)
        return HttpResponseBadRequest(submission.errors.as_json())

    def _handle_update(self, project, user_project):
        """
        Handle requirements status changes.
        """
        request = self.request
        user = request.user
        redirect_url = reverse('projects:detail_user',
                               args=[project.slug, project.pk, user.username])

        # deepcopy to preserve the original state
        requirements = copy.deepcopy(user_project.requirements)
        max_progress = user_project.requirements_completed_percent_max

        if requirements:
            # create a copy and modify this instead so we can compare it later
            requirements_copy = copy.deepcopy(requirements)

            # update requirements_copy
            updated_reqs = [int(r) for r in request.POST.getlist('reqs', [])]

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

            _, progress_after, become_complete, _ = UserProject.requirements_diff(
                requirements, requirements_copy)
            # only create progress update event when progress_after > progress_before
            if progress_after > float(max_progress):
                for msg in become_complete:
                    user_project.add_event(
                        UserProjectEvent.TYPE_PROGRESS_UPDATE,
                        message=msg)

            # if all requirements completed, ready for review
            if user_project.is_requirements_complete():
                messages.info(request,
                              "Mantap! Proyek kamu siap untuk direview",
                              extra_tags='success')

        return HttpResponseRedirect(redirect_url)

    def _handle_review_request(self, project, user_project):
        request = self.request
        user = request.user

        redirect_url = reverse('projects:detail_user',
                               args=[project.slug, project.pk, user.username])
        form = UserProjectReviewRequestForm(
            request.POST, instance=user_project)

        if form.is_valid():
            review_requested = form.submit_review()
            if review_requested:
                user_project.add_event(UserProjectEvent.TYPE_REVIEW_REQUEST)
                messages.info(request,
                              "Terima kasih! Proyek kamu akan segera direview team UpKoding.",
                              extra_tags='success')
            else:
                messages.info(request,
                              "Detail proyek berhasil diupdate!",
                              extra_tags='success')
            return HttpResponseRedirect(redirect_url)

        self.object = self.get_object()
        context = self.get_context_data(**self.kwargs)
        context['review_request_form'] = form
        return render(request, self.template_name, context)

    def _handle_delete(self, project, user_project):
        if user_project.can_delete():
            user_project.delete()
            messages.info(self.request, 'Tantangan telah dibatalkan.',
                          extra_tags='warning')
            return HttpResponse(project.get_absolute_url())
        else:
            messages.info(self.request, 'Tantangan hanya bisa dibatalkan 24 jam setelah dimulai. Ayolah kamu pasti bisa!',
                          extra_tags='danger')
            return HttpResponse(user_project.get_absolute_url())

    @method_decorator(login_required)
    def post(self, request, slug, pk, username):
        user = request.user
        if user.username != username:
            return HttpResponseForbidden()

        action = request.POST.get('action')
        project = self.get_object()
        user_project = get_object_or_404(
            UserProject, user=user, project=project)

        if action == 'code_submission':
            return self._handle_code_submission(project, user_project)

        if action == 'update':
            return self._handle_update(project, user_project)

        if action == 'delete':
            return self._handle_delete(project, user_project)

        if action == 'review_request':
            return self._handle_review_request(project, user_project)
        return HttpResponseRedirect(project.get_absolute_url())
