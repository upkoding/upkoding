from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectList.as_view(), name='list'),
    path('<int:pk>/<slug:slug>/', views.ProjectDetail.as_view(), name='detail'),
    path('<int:pk>/', views.ProjectDetail.as_view(), name='detail-redirect'),
]
