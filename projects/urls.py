from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('<slug:slug>-<int:pk>/', views.ProjectDetail.as_view(), name='detail'),
    path('', views.ProjectList.as_view(), name='list'),
]
