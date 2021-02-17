from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.contrib import messages

from account.models import User
from .models import Project


class ProjectList(ListView):
    queryset = Project.objects.filter(is_active=True)


class ProjectDetail(DetailView):
    queryset = Project.objects.filter(is_active=True)

    def get_object(self):
        """
        We need to find object by using `pk` and `slug`.
        """
        return get_object_or_404(
            Project,
            pk=self.kwargs.get('pk'),
            slug=self.kwargs.get('slug'),
            is_active=True
        )

    def post(self, request, **kwargs):
        user = request.user
        next_url = reverse('projects:detail', args=[
            kwargs.get('slug'), kwargs.get('pk')
        ])
        # not authenticated, ask for login
        if not user.is_authenticated:
            messages.warning(
                request,
                'Silahkan login terlebih dahulu sebelum mengerjakan proyek.'
            )
            return HttpResponseRedirect(reverse('account:login') + '?next={}'.format(next_url))

        # create user project
        success_url = reverse('projects:detail_user', args=[
            kwargs.get('slug'), kwargs.get('pk'), user.username
        ])
        return HttpResponseRedirect(success_url)


class ProjectDetailUser(DetailView):
    queryset = Project.objects.filter(is_active=True)
    template_name = 'projects/project_detail_user.html'

    def get_object(self):
        """
        We need to find object by using `pk` and `slug`.
        """
        return get_object_or_404(
            Project,
            pk=self.kwargs.get('pk'),
            slug=self.kwargs.get('slug'),
            is_active=True
        )

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        data = super().get_context_data(**kwargs)
        data['project_user'] = user
        return data
