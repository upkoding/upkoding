from django.urls import path

from .views import Index, TopicDetail, CreateTopicThread, ThreadDetail

app_name = 'forum'


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('<slug:slug>/',
         TopicDetail.as_view(), name='topic'),
    path('<slug:slug>/',
         CreateTopicThread.as_view(), name='new_thread'),
    path('<slug:topic_slug>/<slug:slug>-<int:pk>/',
         ThreadDetail.as_view(), name='thread'),
]
