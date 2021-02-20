from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import UserProject


class UserProjectCompletionForm(forms.ModelForm):
    kind = forms.CharField(widget=forms.HiddenInput(), initial='complete')

    class Meta:
        model = UserProject
        fields = ['demo_url', 'sourcecode_url', 'note']

    def clean_demo_url(self):
        url = self.cleaned_data['demo_url']
        if self.instance.require_demo_url and not url:
            raise ValidationError('URL Proyek harus diisi')
        return url

    def clean_sourcecode_url(self):
        url = self.cleaned_data['sourcecode_url']
        if self.instance.require_sourcecode_url and not url:
            raise ValidationError('URL kode sumber proyek harus diisi')
        return url

    def complete(self):
        """
        A shortcut to set `project_completed` to True and save the project.
        Returns Boolean whether user earned a point or not, point only earned the first time
        user complete this project, updating completion form won't.
        """
        if self.instance.project_completed:
            self.save()
            return False

        # TODO: Add point to user with transaction
        user_project = self.save(commit=False)
        user_project.project_completed = True
        user_project.save()
        return True
