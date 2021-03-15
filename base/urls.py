from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

from .views import render_template, Index

app_name = 'base'


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('diskusi/', render_template('base/forum.html'), name='forum'),
    path('tentang/', render_template('base/tentang.html'), name='tentang'),
    path('robots.txt', render_template('base/robots.txt', 'text/plain')),
]
