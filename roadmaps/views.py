import logging
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Roadmap, RoadmapTopic

log = logging.getLogger(__file__)


class RoadmapList(ListView):
    queryset = Roadmap.objects.filter(status=Roadmap.STATUS_ACTIVE)


class RoadmapDetail(DetailView):
    model = Roadmap

    def get_object(self):
        user = self.request.user
        obj = get_object_or_404(
            Roadmap,
            slug=self.kwargs.get('slug'),
        )
        # - allow staff to preview inactive project
        # - or if its active
        if user.is_staff or obj.is_active():
            return obj
        raise Http404()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        roadmap = data.get('object')
        topics = RoadmapTopic.objects \
            .filter(roadmap=roadmap, status=RoadmapTopic.STATUS_ACTIVE) \
            .prefetch_related('contents__content_object')
        data['topics'] = topics
        return data
