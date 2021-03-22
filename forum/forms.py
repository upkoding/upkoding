from django import forms

from account.models import User
from .models import Topic, Thread, ThreadAnswer


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'description']

    def __init__(self, user: User, topic: Topic, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.topic = topic

    def save(self, *args, **kwargs):
        thread = super().save(commit=False)
        thread.user = self.user
        thread.topic = self.topic
        thread.save()


class ThreadAnswerForm(forms.ModelForm):
    class Meta:
        model = ThreadAnswer
        fields = ['message']

    def __init__(self, user: User, thread: Thread, *args, parent: ThreadAnswer = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.thread = thread
        self.parent = parent

    def save(self, *args, **kwargs):
        answer = super().save(commit=False)
        answer.user = self.user
        answer.thread = self.thread
        answer.parent = self.parent
        answer.save()
