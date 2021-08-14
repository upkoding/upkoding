from django import forms
from django.core.exceptions import ValidationError

from codeblocks.models import CodeBlock
from .models import UserProject


class UserProjectCodeSubmissionForm(forms.Form):
    code_block_id = forms.IntegerField()
    code_block = forms.CharField()

    def __init__(self, codeblock: CodeBlock, *args, **kwargs):
        self.codeblock = codeblock
        super().__init__(*args, **kwargs)

    def clean_code_block_id(self):
        block_id = self.cleaned_data['code_block_id']
        if (block_id < 1) or (block_id > CodeBlock.NUM_BLOCKS):
            raise ValidationError('Blok kode tidak sesuai')
        is_readonly = getattr(self.codeblock, f'block_{block_id}_ro')
        if is_readonly:
            raise ValidationError('Blok kode tidak sesuai')
        return block_id

    def run(self):
        # save code block
        code_block_id = self.cleaned_data['code_block_id']
        code_block = self.cleaned_data['code_block']
        setattr(self.codeblock, f'block_{code_block_id}_code', code_block)
        self.codeblock.save()
        self.codeblock.run_source_code()
        return self.codeblock.run_result_summary()


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
