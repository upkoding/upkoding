from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import views
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from projects.models import UserProject, UserProjectEvent
from .forms import ProfileForm, LinkForm, EmailNotificationSettings, StaffEmailNotificationSettings


class LoginView(views.LoginView):
    template_name = 'account/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('base:index'))
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


class ProfileView(LoginRequiredMixin, View):
    def __render(self, request, profile_form, link_form):
        return render(request, 'account/profile.html', {
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

        if kind == ProfileForm.NAME:
            form = ProfileForm(
                request.POST, request.FILES, instance=request.user)
            if not form.is_valid():
                link_form = LinkForm(user, instance=user.get_link())
                return self.__render(request, form, link_form)

            form.save()
            messages.info(self.request, 'Profil berhasil disimpan!',
                          extra_tags='success')

        if kind == LinkForm.NAME:
            form = LinkForm(user, request.POST, instance=user.get_link())
            if not form.is_valid():
                profile_form = ProfileForm(instance=user)
                return self.__render(request, profile_form, form)

            form.save()
            messages.info(self.request, 'Links berhasil disimpan!',
                          extra_tags='success')

        return HttpResponseRedirect(reverse('account:profile'))


class SettingsView(LoginRequiredMixin, View):

    def __render(self, request, email_notification_form):
        return render(request, 'account/settings.html', {
            'email_notification_form': email_notification_form,
        })

    def get(self, request):
        user = request.user
        email_notification_form = StaffEmailNotificationSettings(
            user) if user.is_staff else EmailNotificationSettings(user)
        email_notification_form.load()

        return self.__render(request, email_notification_form)

    def post(self, request):
        user = request.user
        kind = request.POST.get('kind')

        if kind == EmailNotificationSettings.NAME:
            form = StaffEmailNotificationSettings(
                user, request.POST) if user.is_staff else EmailNotificationSettings(user, request.POST)
            if form.is_valid():
                form.save()
                messages.info(self.request, 'Pengaturan notifikasi berhasil disimpan!',
                              extra_tags='success')

        return HttpResponseRedirect(reverse('account:settings'))


class ProStatusView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'account/pro.html')
