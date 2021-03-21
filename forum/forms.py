from django import forms

from .models import Thread, ThreadAnswer


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread


class ThreadAnswerForm(forms.ModelForm):
    class Meta:
        model = ThreadAnswer
