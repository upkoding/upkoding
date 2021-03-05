from django.forms import Textarea


class ProjectRequirementsWidget(Textarea):
    """
    Custom Textarea to input project requirements easily.
    """
    template_name = 'projects/forms/widgets/project_requirements.html'

    class Media:
        js = ('https://cdn.jsdelivr.net/gh/alpinejs/alpine@v2.8.0/dist/alpine.min.js',)
