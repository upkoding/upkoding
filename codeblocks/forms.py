from django import forms
from django_ace import AceWidget

from .models import CodeBlock


class CodeBlockAdminForm(forms.ModelForm):
    class Meta:
        model = CodeBlock
        widgets = {
            'block_1_code': AceWidget(width='600px'),
            'block_2_code': AceWidget(width='600px'),
            'block_3_code': AceWidget(width='600px'),
            'block_4_code': AceWidget(width='600px'),
            'block_5_code': AceWidget(width='600px'),
            'run_result': AceWidget(mode='json', width='600px', readonly=True),
        }
        fields = '__all__'
