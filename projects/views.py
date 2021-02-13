from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from account.models import User
from .models import Project


class ProjectList(ListView):
    queryset = Project.objects.all()


class ProjectDetail(DetailView):
    queryset = Project.objects.all()

    def get_object(self):
        """
        We need to find object by using `pk` and `slug`.
        """
        return get_object_or_404(
            Project,
            pk=self.kwargs.get('pk'),
            slug=self.kwargs.get('slug')
        )


class ProjectDetailUser(DetailView):
    queryset = Project.objects.all()
    template_name = 'projects/project_detail_user.html'

    def get_object(self):
        """
        We need to find object by using `pk` and `slug`.
        """
        return get_object_or_404(
            Project,
            pk=self.kwargs.get('pk'),
            slug=self.kwargs.get('slug')
        )

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        data = super().get_context_data(**kwargs)
        data['project_user'] = user
        return data
