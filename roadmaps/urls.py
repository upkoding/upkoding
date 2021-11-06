from django.urls import path

from .views import RoadmapList, RoadmapDetail

app_name = 'roadmaps'

urlpatterns = [
    path('<slug:slug>/', RoadmapDetail.as_view(), name='detail'),
    path('', RoadmapList.as_view(), name='list'),
]
