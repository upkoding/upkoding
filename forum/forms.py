from django import forms

from account.models import User
from .models import Topic, Thread, ThreadAnswer


class ThreadForm(forms.ModelForm):
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.filter(status=Topic.STATUS_ACTIVE))

    class Meta:
        model = Thread
        fields = ['topic', 'title', 'description']

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, *args, **kwargs):
        thread = super().save(commit=False)
        thread.user = self.user
        thread.save()


class ThreadUpdateForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'description']


class ThreadAnswerForm(forms.ModelForm):
    thread = forms.ModelChoiceField(
        queryset=Thread.objects.filter(status=Thread.STATUS_ACTIVE))
    parent = forms.ModelChoiceField(
        required=False,
        queryset=ThreadAnswer.objects.filter(status=ThreadAnswer.STATUS_ACTIVE))

    class Meta:
        model = ThreadAnswer
        fields = ['thread', 'parent', 'message']

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, *args, **kwargs):
        answer = super().save(commit=False)
        answer.user = self.user
        answer.save()


class ThreadAnswerUpdateForm(forms.ModelForm):
    class Meta:
        model = ThreadAnswer
        fields = ['message']
