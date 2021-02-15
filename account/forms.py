from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UsernameField

from .models import User, Link


USERNAME_VALIDATORS = [
    RegexValidator(
        regex='^[a-zA-Z0-9_]*$',
        message='Format username tidak valid'),
]


class ProfileForm(forms.ModelForm):
    """
    Customized profile form to match Bootstrap 5 styles.
    """
    username = UsernameField(required=True,
                             label='Username *',
                             validators=USERNAME_VALIDATORS,
                             help_text="Karakter yang diperbolehkan: huruf, angka dan _ (underscore)")
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
