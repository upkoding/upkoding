from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    # complete namespace: account:social
    path('', include('social_django.urls', namespace='social')),
    path('', views.IndexView.as_view(), name='index'),
]
