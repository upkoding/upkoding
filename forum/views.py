from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Topic, Thread, ThreadAnswer
from .forms import ThreadForm, ThreadAnswerForm


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
            status=Thread.STATUS_ACTIVE)[:10]
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


class CreateTopicThread(LoginRequiredMixin, DetailView):
    queryset = Topic.objects.filter(status=Topic.STATUS_ACTIVE)

    def post(self, request, slug):
        user = request.user
        topic = self.get_object()
        form = ThreadForm(user, topic, request.POST)

        if form.is_valid():
            form.save()
            return render(request, 'forum/_thread_item.html', {'thread': form.instance, 'topic': topic})
        return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json; charset=utf-8')
