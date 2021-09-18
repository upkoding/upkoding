from django import forms
from django.core.exceptions import ValidationError

from account.models import User
from codeblocks.models import CodeBlock
from .models import Project, UserProject


class UserProjectCodeSubmissionForm(forms.Form):
    code_block_id = forms.IntegerField()
    code_block = forms.CharField()

    def __init__(self, user: User, project: Project, user_project: UserProject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.project = project
        self.user_project = user_project
        self.codeblock = user_project.codeblock

    def clean(self):
        cleaned_data = super().clean()

        if self.project.is_premium and not self.user.is_pro_user():
            raise ValidationError('Maaf, ini adalah tantangan premium diperlukan Pro Access menjalankan.',
                                  code='error_access')

        if not self.user_project.can_run_codeblock(self.user):
            raise ValidationError('Batas menjalankan kode tercapai, tunggu 24 jam atau gunakan PRO Access.',
                                  code='error_limit')

        block_id = cleaned_data['code_block_id']
        if (block_id < 1) or (block_id > CodeBlock.NUM_BLOCKS):
            raise ValidationError('Blok kode tidak sesuai',
                                  code='error_validation')

        is_readonly = getattr(self.codeblock, f'block_{block_id}_ro')
        if is_readonly:
            raise ValidationError('Blok kode readonly',
                                  code='error_validation')
        return cleaned_data

    def run(self):
        # save code block
        code_block_id = self.cleaned_data['code_block_id']
        code_block = self.cleaned_data['code_block']
        setattr(self.codeblock, f'block_{code_block_id}_code', code_block)
        self.codeblock.save()
        self.codeblock.run_source_code()

        # make sure it returns the latest state
        self.codeblock.refresh_from_db()
        return self.codeblock


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
