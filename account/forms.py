from django import forms
from django.contrib.auth.forms import UsernameField
from django.core.validators import RegexValidator

from .models import User, Link, UserSetting

USERNAME_VALIDATORS = [
    RegexValidator(
        regex='^[a-zA-Z0-9_]{3,}$',
        message='Format username tidak valid'),
]


class ProfileForm(forms.ModelForm):
    """
    Customized profile form to match Bootstrap 5 styles.
    """
    NAME = 'profile_form'
    kind = forms.CharField(widget=forms.HiddenInput(), initial=NAME)

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
                  'first_name', 'description']

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
    NAME = 'links_form'
    kind = forms.CharField(widget=forms.HiddenInput(), initial=NAME)

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
    NAME = 'email_notification_settings'
    kind = forms.CharField(widget=forms.HiddenInput(), initial=NAME)

    email_notify_project_message = forms.BooleanField(
        label='Percakapan di timeline proyek',
        required=False)
    email_notify_project_approved = forms.BooleanField(
        label='Proyek saya disetujui',
        required=False)
    email_notify_project_disapproved = forms.BooleanField(
        label='Proyek saya tidak disetujui',
        required=False)
    email_notify_forum_activity = forms.BooleanField(
        label='Aktivitas di forum',
        required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def load(self):
        # load initial value from DB
        for name in self.fields:
            if name == 'kind':
                continue
            field = self.fields.get(name)
            field.initial = getattr(UserSetting.objects, name)(self.user)

    def save(self):
        for name in self.cleaned_data:
            if name == 'kind':
                continue
            value = self.cleaned_data.get(name)
            getattr(UserSetting.objects, name)(self.user, value)


class StaffEmailNotificationSettings(EmailNotificationSettings):
    email_notify_project_review_request = forms.BooleanField(
        label='Permintaan review proyek', help_text='Hanya untuk proyek yang saya buat (staff).', required=False)
