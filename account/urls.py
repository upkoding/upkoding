from django.urls import path, include

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.signin, name='login'),
    path('logout/', views.signout, name='logout'),
    path('profile/', views.profile, name='profile'),
]
