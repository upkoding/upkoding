import logging
import json
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from projects.models import UserProject, UserProjectEvent
from .midtrans import is_payment_notification_valid
from .models import ProAccessPurchase, MidtransPaymentNotification
from .forms import (
    get_form_error,
    ProfileForm,
    LinkForm,
    EmailNotificationSettings,
    StaffEmailNotificationSettings,
    ProAccessPurchaseForm,
    ProAccessPurchaseActionForm,
)

log = logging.getLogger(__file__)


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


class ProfileFormView(LoginRequiredMixin, View):
    def __render(self, request, form,):
        return render(request, 'account/form_profile.html', {'form': form})

    def get(self, request):
        form = ProfileForm(instance=request.user)
        return self.__render(request, form)

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if not form.is_valid():
            return self.__render(request, form)

        form.save()
        messages.info(request, 'Profil berhasil disimpan!',
                      extra_tags='success')

        return HttpResponseRedirect(reverse('account:profile'))


class LinksFormView(LoginRequiredMixin, View):
    def __render(self, request, form):
        return render(request, 'account/form_links.html', {'form': form})

    def get(self, request):
        user = request.user
        form = LinkForm(user, instance=user.get_link())
        return self.__render(request, form)

    def post(self, request):
        user = request.user
        form = LinkForm(user, request.POST, instance=user.get_link())
        if not form.is_valid():
            return self.__render(request, form)

        form.save()
        messages.info(request, 'Links berhasil disimpan!',
                      extra_tags='success')

        return HttpResponseRedirect(reverse('account:links'))


class AuthenticationMethodFormView(LoginRequiredMixin, TemplateView):
    template_name = 'account/form_auths.html'


class NotificationFormView(LoginRequiredMixin, View):

    def __render(self, request, form):
        return render(request, 'account/form_notifications.html', {
            'form': form,
        })

    def get(self, request):
        user = request.user
        form = StaffEmailNotificationSettings(
            user) if user.is_staff else EmailNotificationSettings(user)
        form.load()

        return self.__render(request, form)

    def post(self, request):
        user = request.user
        form = StaffEmailNotificationSettings(
            user, request.POST) if user.is_staff else EmailNotificationSettings(user, request.POST)
        if form.is_valid():
            form.save()
            messages.info(self.request, 'Pengaturan notifikasi berhasil disimpan!',
                          extra_tags='success')

        return HttpResponseRedirect(reverse('account:notifications'))


class ProStatusView(LoginRequiredMixin, View):

    def _render(self, request, **kwargs):
        selected_plan = request.GET.get('plan')

        # get pro access for user, if end-date never set
        # consider it doesn't exist.
        try:
            pro_access = request.user.pro_access
            if pro_access and not pro_access.end:
                pro_access = None
        except Exception:
            pro_access = None

        purchases = ProAccessPurchase.objects \
            .filter(user=request.user)

        return render(request, 'account/form_pro.html', {
            'selected_plan': selected_plan,
            'pro_access': pro_access,
            'purchases': purchases,
            **kwargs
        })

    def get(self, request):
        return self._render(request)

    def post(self, request):
        user = request.user
        form = ProAccessPurchaseForm(user, request.POST)
        if form.is_valid():
            form.purchase_access()
            messages.info(self.request, 'Order telah dibuat, silahkan lanjutkan dengan pembayaran.',
                          extra_tags='success')
            return HttpResponseRedirect(reverse('account:pro'))

        error_message = get_form_error(form)
        if error_message:
            messages.info(self.request, error_message, extra_tags='warning')
        return self._render(request, form=form)


@login_required
def purchase_cancel(request):
    form = ProAccessPurchaseActionForm(request.user, request.POST)
    if form.is_valid():
        purchase_id = form.cleaned_data.get('purchase_id')
        try:
            form.cancel_purchase()
            messages.info(request, f'Order Pro Access dengan ID={purchase_id} telah dibatalkan.',
                          extra_tags='success')
        except Exception:
            messages.info(request, f'Maaf terjadi error ketika membatalkan order Pro Access dengan ID={purchase_id}.',
                          extra_tags='danger')
    else:
        error_message = get_form_error(form)
        if error_message:
            messages.info(request, error_message, extra_tags='warning')
    return HttpResponseRedirect(reverse('account:pro'))


@login_required
def purchase_payment(request):
    form = ProAccessPurchaseActionForm(request.user, request.POST)
    if form.is_valid():
        try:
            payment_url = form.get_midtrans_redirect_url()
            return HttpResponseRedirect(payment_url)
        except Exception as e:
            log.error(str(e))
            messages.info(request, f'Maaf terjadi error ketika membuat link pembayaran Midtrans.',
                          extra_tags='danger')
    else:
        error_message = get_form_error(form)
        if error_message:
            messages.info(request, error_message, extra_tags='warning')
    return HttpResponseRedirect(reverse('account:pro'))


@csrf_exempt
def midtrans_payment_notification(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        is_valid = is_payment_notification_valid(payload)
        if is_valid:
            MidtransPaymentNotification.create_from_payload(payload)
            return HttpResponse()
        return HttpResponseBadRequest('Notification payload invalid')

    return HttpResponseRedirect(reverse('account:pro'))
