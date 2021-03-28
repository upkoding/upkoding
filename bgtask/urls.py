from django.urls import path

from .views import TaskHandler

app_name = 'bgtask'

urlpatterns = [
    path('<str:key>', TaskHandler.as_view(), name='index'),
]
