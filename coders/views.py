from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from account.models import User


class CoderList(ListView):
    template_name = 'coders/coder_list.html'
    queryset = User.objects.all()


class CoderDetail(DetailView):
    template_name = 'coders/coder_detail.html'
    queryset = User.objects.all()

    def get_object(self):
        """
        We need to find object by using `username`
        """
        return get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
