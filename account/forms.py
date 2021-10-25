from django import forms
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import transaction

from upkoding import pricing
from .models import User, Link, UserSetting, ProAccess, ProAccessPurchase
from .midtrans import get_redirect_url

USERNAME_VALIDATORS = [
    RegexValidator(
        regex='^[a-zA-Z0-9_]{3,}$',
        message='Format username tidak valid'),
]


def get_form_error(form, field='__all__'):
    message = None
    all_errors = form.errors.as_data().get(field)
    if all_errors:
        message = all_errors[0].message
    return message


class ProfileForm(forms.ModelForm):
    """
    Customized profile form to match Bootstrap 5 styles.
    """
    username = UsernameField(required=True,
                             label='Username *',
                             validators=USERNAME_VALIDATORS,
                             help_text="Minimum 3 karakter (huruf, angka dan _ diperbolehkan)")
    email = forms.EmailField(required=True,
                             label='Alamat Email *')
    first_name = forms.CharField(required=True,
                                 label='Nama *')
    description = forms.CharField(required=True,
                                  label='Tentang *',
                                  help_text="Format = Markdown",
                                  widget=forms.Textarea())

    class Meta:
        model = User
        fields = ['avatar', 'username', 'email',
                  'first_name', 'description', 'time_zone']

    def is_valid(self):
        """
        Add bootstrap `is-invalid` class to form input when its invalid.
        """
        result = super().is_valid()
        fields = self.fields
        errors = self.errors
        for field in errors:
            attrs = fields[field].widget.attrs
            attrs.update(
                {'class': attrs.get('class', '') + ' is-invalid'}
            )
        return result


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ('user',)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, *args, **kwargs):
        link = super().save(commit=False)
        link.user = self.user
        link.save()


class EmailNotificationSettings(forms.Form):
    email_notify_project_message = forms.BooleanField(
        label='Percakapan di timeline proyek',
        required=False)
    email_notify_project_approved = forms.BooleanField(
        label='Proyek saya disetujui',
        required=False)
    email_notify_project_disapproved = forms.BooleanField(
        label='Proyek saya tidak disetujui',
        required=False)
    # email_notify_forum_activity = forms.BooleanField(
    #     label='Aktivitas di forum',
    #     required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def load(self):
        # load initial value from DB
        for name in self.fields:
            field = self.fields.get(name)
            field.initial = getattr(UserSetting.objects, name)(self.user)

    def save(self):
        for name in self.cleaned_data:
            value = self.cleaned_data.get(name)
            getattr(UserSetting.objects, name)(self.user, value)


class StaffEmailNotificationSettings(EmailNotificationSettings):
    email_notify_project_review_request = forms.BooleanField(
        label='Permintaan review proyek (for staff only)', required=False)


class ProAccessPurchaseForm(forms.Form):
    plan_id = forms.CharField()

    def __init__(self, user: User, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        plan_id = cleaned_data.get('plan_id')

        # make sure plan ID is valid
        if not pricing.plan_id_is_valid(plan_id):
            raise forms.ValidationError(
                'Maaf, paket yang dipilih tidak valid!')

        # TODO: remove this after beta
        if self.user.is_pro_user():
            raise forms.ValidationError(
                'Pro Access bisa diperpanjang setelah periode saat ini sudah habis.')

        # make sure user doesn't have PENDING purchase
        if not ProAccessPurchase.can_create(self.user):
            raise forms.ValidationError(
                'Terdapat order yang masih pending, '
                'batalkan atau lanjutkan ke pembayaran sebelum membuat yang baru.')

        return cleaned_data

    def purchase_access(self, is_beta: bool = False):
        with transaction.atomic():
            pro_access, _ = ProAccess.objects.get_or_create(user=self.user)
            plan = pricing.get_plan(self.cleaned_data.get('plan_id'))
            pro_access_purchase = ProAccessPurchase(
                user=self.user,
                pro_access=pro_access,
                plan_name=plan.name,
                days=plan.access_days,
                price=plan.price,
            )
            pro_access_purchase.save()

            # TODO: remove this after beta
            if is_beta:
                pro_access_purchase.set_gifted()



class ProAccessPurchaseActionForm(forms.Form):
    ACTION_CANCEL = 'cancel'
    ACTION_PAY = 'pay'
    ACTIONS = [
        (ACTION_CANCEL, ACTION_CANCEL),
        (ACTION_PAY, ACTION_PAY),
    ]

    purchase_id = forms.UUIDField()
    purchase_action = forms.ChoiceField(choices=ACTIONS)

    def __init__(self, user: User, *args, **kwargs):
        self.user = user
        self.purchase = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # make sure it belongs to current user
        try:
            self.purchase = ProAccessPurchase.objects.get(
                pk=cleaned_data.get('purchase_id'),
                user=self.user
            )
        except ProAccessPurchase.DoesNotExist:
            raise ValidationError('Order ID tidak valid!')

        # make sure it payable and cancelable
        if not self.purchase.can_pay():
            raise ValidationError('Order sudah kadaluarsa!')

        return cleaned_data

    def cancel_purchase(self):
        self.purchase.set_canceled()

    def get_midtrans_redirect_url(self):
        return get_redirect_url(
            order_id=str(self.purchase.pk),
            order_name=self.purchase.plan_name,
            gross_amount=self.purchase.price,
            customer_first_name=self.user.first_name,
            customer_last_name=self.user.last_name,
            customer_email=self.user.email
        )
