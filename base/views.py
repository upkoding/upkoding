from django.views.generic.base import TemplateView

from projects.models import Project, UserProject


def render_template(name, content_type="text/html; charset=utf-8"):
    """
    Just a shortcuts method.
    """
    return TemplateView.as_view(template_name=name, content_type=content_type)


class Index(TemplateView):
    template_name = 'base/index.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['projects'] = Project.objects.active()[:3]
        data['user_projects_inprogress'] = UserProject.objects.filter(
            status__in=(UserProject.STATUS_IN_PROGRESS,
                        UserProject.STATUS_PENDING_REVIEW,
                        UserProject.STATUS_INCOMPLETE)
        ).order_by('-updated')[:5]
        data['user_projects_completed'] = UserProject.objects.filter(
            status=UserProject.STATUS_COMPLETE
        ).order_by('-updated')[:5]
        return data
