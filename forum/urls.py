from django.urls import path

from .views import (
    PageIndex,
    PageThreadDetail,
    PageTopicDetail,
    ApiThreads,
    ApiThreadDetail,
    ApiAnswers,
    ApiAnswerDetail,
)

app_name = 'forum'


urlpatterns = [
    # page paths
    path('', PageIndex.as_view(), name='index'),
    path('<slug:slug>/',
         PageTopicDetail.as_view(), name='topic_detail'),
    path('<slug:topic_slug>/<slug:slug>-<int:pk>/',
         PageThreadDetail.as_view(), name='thread_detail'),

    # API paths
    path('api/threads/',
         ApiThreads.as_view(), name='api_threads'),
    path('api/threads/<int:pk>/',
         ApiThreadDetail.as_view(), name='api_thread_detail'),
    path('api/answers/',
         ApiAnswers.as_view(), name='api_answers'),
    path('api/answers/<int:pk>/',
         ApiAnswerDetail.as_view(), name='api_answer_detail'),
]
