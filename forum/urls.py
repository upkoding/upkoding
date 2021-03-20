from django.urls import path

from .views import Index, TopicDetail, ThreadDetail

app_name = 'forum'


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('<slug:slug>/',
         TopicDetail.as_view(), name='topic'),
    path('<slug:topic_slug>/<slug:slug>-<int:pk>/',
         ThreadDetail.as_view(), name='thread'),
]
