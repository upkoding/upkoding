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
        data['featured_projects'] = Project.objects.featured()
        # data['user_project_feeds'] = UserProject.objects\
        #     .select_related('user', 'project')\
        #     .filter(status__in=[UserProject.STATUS_IN_PROGRESS, UserProject.STATUS_COMPLETE])[:6]
        return data
