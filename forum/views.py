# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.db.models.query import Prefetch
# from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
# from django.shortcuts import get_object_or_404, render
# from django.views.generic import TemplateView, DetailView
# from django.views.generic.base import View

# from .forms import ThreadForm, ThreadUpdateForm, ThreadAnswerForm, ThreadAnswerUpdateForm
# from .models import Topic, Thread, ThreadAnswer


# class PageIndex(TemplateView):
#     template_name = 'forum/index.html'

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['top_topics'] = Topic.objects.filter(status=Topic.STATUS_ACTIVE)[:5]
#         data['latest_threads'] = Thread.objects.select_related('user', 'topic').filter(status=Thread.STATUS_ACTIVE)[:5]
#         return data


# class PageTopicDetail(DetailView):
#     queryset = Topic.objects.filter(status=Topic.STATUS_ACTIVE)

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         data['top_threads'] = Thread.objects.select_related('user').filter(
#             topic=self.object,
#             status=Topic.STATUS_ACTIVE)[:5]
#         data['latest_threads'] = Thread.objects.select_related('user').filter(
#             topic=self.object,
#             status=Thread.STATUS_ACTIVE)[:10]
#         return data


# class PageThreadDetail(DetailView):
#     queryset = Thread.objects.filter(status=Thread.STATUS_ACTIVE)

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         thread = self.object
#         data['edit_thread'] = int(self.request.GET.get('edit_thread', 0))
#         data['edit_answer'] = int(self.request.GET.get('edit_answer', 0))

#         # TODO: paginate results
#         data['answers'] = ThreadAnswer.objects \
#             .select_related('user') \
#             .prefetch_related(Prefetch('replies', queryset=ThreadAnswer.objects.active())) \
#             .filter(thread=thread, parent=None, status=ThreadAnswer.STATUS_ACTIVE)

#         data['related_threads'] = Thread.objects.select_related('user').filter(
#             topic=thread.topic,
#             status=Thread.STATUS_ACTIVE)[:10]
#         return data


# class ApiThreads(LoginRequiredMixin, View):

#     def post(self, request):
#         user = request.user
#         form = ThreadForm(user, request.POST)

#         if form.is_valid():
#             form.save()
#             instance = form.instance
#             return render(request, 'forum/_thread_item_card.html',
#                           {'thread': instance, 'topic': instance.topic, 'full': True})
#         return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json; charset=utf-8')


# class ApiThreadDetail(LoginRequiredMixin, View):

#     def post(self, request, pk):
#         user = request.user
#         thread = get_object_or_404(Thread, status=Thread.STATUS_ACTIVE, pk=pk)

#         # only owner can update
#         if user != thread.user:
#             return HttpResponseForbidden()

#         form = ThreadUpdateForm(request.POST, instance=thread)
#         if form.is_valid():
#             form.save()
#             return HttpResponse()
#         return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json; charset=utf-8')

#     def delete(self, request, pk):
#         user = request.user
#         thread = get_object_or_404(Thread, status=Thread.STATUS_ACTIVE, pk=pk)

#         # only owner can update
#         if user != thread.user:
#             return HttpResponseForbidden()

#         # soft delete
#         thread.status = Thread.STATUS_INACTIVE
#         thread.save()
#         return HttpResponse()


# class ApiAnswers(LoginRequiredMixin, View):

#     def post(self, request):
#         user = request.user

#         form = ThreadAnswerForm(user, request.POST)
#         if form.is_valid():
#             form.save()
#             instance = form.instance

#             if instance.parent:
#                 # reply to an answer
#                 return render(request, 'forum/_answer_item_replies_item.html',
#                               {'answer': instance, 'thread': instance.thread})
#             else:
#                 # answer to thread
#                 return render(request, 'forum/_answer_item.html',
#                               {'answer': instance, 'thread': instance.thread, 'edit_thread': 0, 'edit_answer': 0})
#         return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json; charset=utf-8')


# class ApiAnswerDetail(LoginRequiredMixin, View):

#     def post(self, request, pk):
#         user = request.user
#         answer = get_object_or_404(ThreadAnswer, status=ThreadAnswer.STATUS_ACTIVE, pk=pk)

#         # only owner can update
#         if user != answer.user:
#             return HttpResponseForbidden()

#         form = ThreadAnswerUpdateForm(request.POST, instance=answer)
#         if form.is_valid():
#             form.save()
#             return HttpResponse()
#         return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json; charset=utf-8')

#     def delete(self, request, pk):
#         user = request.user
#         answer = get_object_or_404(ThreadAnswer, status=ThreadAnswer.STATUS_ACTIVE, pk=pk)

#         # only owner can delete
#         if user != answer.user:
#             return HttpResponseForbidden()

#         # soft delete
#         answer.status = ThreadAnswer.STATUS_INACTIVE
#         answer.save()

#         return HttpResponse()
