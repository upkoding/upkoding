from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UsernameField

from .models import User


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
                             widget=forms.TextInput(
                                   attrs={'class': 'form-control'}),
                             help_text="Karakter yang diperbolehkan: huruf, angka dan _ (underscore)")
    email = forms.EmailField(required=True,
                             label='Alamat Email *',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True,
                                 label='Nama Depan *',
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False,
                                label='Nama Belakang',
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

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
