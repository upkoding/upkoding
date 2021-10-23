import logging
from django.views.generic.base import TemplateView
from stream_django.enrich import Enrich

from upkoding.activity_feed import feed_manager
from projects.models import Project

log = logging.getLogger(__name__)


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

        try:
            enricher = Enrich(('actor', 'object', 'target'))
            feed = feed_manager.get_global_challenge_feed()
            activities = feed.get(limit=10)['results']
            data['activities'] = enricher.enrich_aggregated_activities(
                activities)
        except Exception as e:
            log.error(e)
        return data
