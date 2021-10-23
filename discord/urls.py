from django.urls import path
from django.views.decorators.csrf import csrf_exempt


from .views import InteractionHandler

app_name = 'discord'


urlpatterns = [
    path('interactions/', csrf_exempt(InteractionHandler.as_view()),
         name='interactions'),
]
