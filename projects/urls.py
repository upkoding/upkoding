from django.urls import path

from .views import project, review

app_name = 'projects'

urlpatterns = [
    path('<slug:slug>-<int:pk>/<str:username>/',
         project.ProjectDetailUser.as_view(), name='detail_user'),
    path('<slug:slug>-<int:pk>/', project.ProjectDetail.as_view(), name='detail'),
    path('<int:pk>/review', review.ProjectReview.as_view(), name='review'),
    path('', project.ProjectList.as_view(), name='list'),
]
