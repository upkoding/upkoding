from django.urls import path, include

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('authentication/', views.authentication, name='auth'),
    path('settings/', views.settings, name='settings'),
]
