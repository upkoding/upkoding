from django.urls import path

from . import views

app_name = 'coders'

urlpatterns = [
    path('<str:username>/', views.CoderDetail.as_view(), name='detail'),
    path('', views.CoderList.as_view(), name='list'),
]
