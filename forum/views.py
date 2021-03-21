from django.shortcuts import render
from django.views.generic import TemplateView, DetailView

from .models import Topic, Thread, ThreadAnswer


class Index(TemplateView):
    template_name = 'forum/index.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['top_topics'] = Topic.objects.filter(
            status=Topic.STATUS_ACTIVE)[:5]
        data['latest_threads'] = Thread.objects.filter(
            status=Thread.STATUS_ACTIVE)[:5]
        return data


class TopicDetail(DetailView):
    queryset = Topic.objects.filter(status=Topic.STATUS_ACTIVE)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['top_threads'] = Thread.objects.filter(
            topic=self.object,
            status=Topic.STATUS_ACTIVE)[:5]
        data['latest_threads'] = Thread.objects.filter(
            topic=self.object,
            status=Thread.STATUS_ACTIVE)[:5]
        return data


class ThreadDetail(DetailView):
    queryset = Thread.objects.filter(status=Thread.STATUS_ACTIVE)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        thread = self.object
        data['answers'] = ThreadAnswer.objects.filter(
            status=ThreadAnswer.STATUS_ACTIVE)[:10]
        data['related_threads'] = Thread.objects.filter(
            topic=thread.topic,
            status=Thread.STATUS_ACTIVE)[:10]
        return data
