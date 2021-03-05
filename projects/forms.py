from django import forms
from django.core.exceptions import ValidationError

from .models import UserProject


class UserProjectReviewRequestForm(forms.ModelForm):
    kind = forms.CharField(widget=forms.HiddenInput(),
                           initial='review_request')

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

    def submit_review(self):
        """
        A shortcut to set `status` to Pending Review and save the project.
        Returns Boolean whether status changed or not
        """
        if self.instance.status >= UserProject.STATUS_PENDING_REVIEW:
            self.save()
            return False

        user_project = self.save(commit=False)
        user_project.status = UserProject.STATUS_PENDING_REVIEW
        user_project.save()
        return True
