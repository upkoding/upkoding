from django import forms

from .models import Project, UserProject


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'requirements', 'cover', 'tags']
