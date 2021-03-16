from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import views
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from projects.models import UserProject, UserProjectEvent
from .forms import ProfileForm, LinkForm


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


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'account/index.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_staff:
            data['projects_pending_review'] = UserProject.objects \
                .filter(status=UserProject.STATUS_PENDING_REVIEW) \
                .exclude(user=user) \
                .order_by('-updated')[:5]

        data['projects'] = UserProject.objects.filter(user=user) \
            .order_by('-updated')[:6]
        data['events'] = UserProjectEvent.objects.filter(event_type=UserProjectEvent.TYPE_REVIEW_MESSAGE, user_project__user=user) \
            .exclude(user=user) \
            .order_by('-updated')[:6]
        return data


class SettingsView(LoginRequiredMixin, View):

    def __render(self, request, profile_form, link_form):
        return render(request, 'account/settings.html', {
            'profile_form': profile_form,
            'link_form': link_form
        })

    def get(self, request):
        user = request.user
        profile_form = ProfileForm(instance=user)
        link_form = LinkForm(user, instance=user.get_link())
        return self.__render(request, profile_form, link_form)

    def post(self, request):
        user = request.user
        kind = request.POST.get('kind')

        if kind == 'profile':
            form = ProfileForm(
                request.POST, request.FILES, instance=request.user)
            if not form.is_valid():
                link_form = LinkForm(user, instance=user.get_link())
                return self.__render(request, form, link_form)

            form.save()
            messages.info(self.request, 'Profile berhasil diupdate!',
                          extra_tags='success')

        if kind == 'link':
            form = LinkForm(user, request.POST, instance=user.get_link())
            if not form.is_valid():
                profile_form = ProfileForm(instance=user)
                return self.__render(request, profile_form, form)

            form.save()
            messages.info(self.request, 'Links berhasil diupdate!',
                          extra_tags='success')

        return HttpResponseRedirect(reverse('account:settings'))
