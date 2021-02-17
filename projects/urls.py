from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('<slug:slug>-<int:pk>/<str:username>/',
         views.ProjectDetailUser.as_view(), name='detail_user'),
    path('<slug:slug>-<int:pk>/', views.ProjectDetail.as_view(), name='detail'),
    path('', views.ProjectList.as_view(), name='list'),
]
