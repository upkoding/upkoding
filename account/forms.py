from django import forms
from django.contrib.auth.forms import UsernameField

from .models import User


class ProfileForm(forms.ModelForm):
    """
    Customized profile form to match Bootstrap 5 styles.
    """
    username = forms.CharField(required=True,
                               label='Username *',
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control'}),
                               help_text="Huruf, angka dan @/./+/-/_")
    first_name = forms.CharField(required=True,
                                 label='Nama Depan *',
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False,
                                label='Nama Belakang',
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
