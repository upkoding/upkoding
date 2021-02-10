from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

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
