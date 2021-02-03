from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'website'

urlpatterns = [
    path('', views.index, name='index'),
    path('tentang/', views.about, name='about'),
    path('login/', views.signin, name='login'),
    path('logout/', views.signout, name='logout'),
]
