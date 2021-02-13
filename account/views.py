from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import auth
from django.contrib.auth import views, forms
from django.contrib import messages
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User
from .forms import ProfileForm


class LoginView(views.LoginView):
    template_name = 'account/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('base:index'))
        return super().dispatch(request, *args, **kwargs)


class LogoutView(views.LogoutView):
    """
    Extends LogoutView to add logout message
    """

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Sampai jumpa di lain kesempatan :)',
                      extra_tags='success')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'account/profile.html'
    success_url = reverse_lazy('account:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.info(self.request, 'Profile berhasil disimpan!',
                      extra_tags='success')
        return super().form_valid(form)


@login_required
def authentication(request):
    return render(request, 'account/authentication.html')


@login_required
def settings(request):
    return render(request, 'account/settings.html')
