from django.urls import path, include

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('authentication/', views.authentication, name='auth'),
    path('settings/', views.settings, name='settings'),
    path('', include('social_django.urls', namespace='social')), # complete namespace: account:social
]
