from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

from .views import render_template

app_name = 'base'


urlpatterns = [
    path('', render_template('base/index.html'), name='index'),
    path('proyek/', render_template('base/proyek.html'), name='proyek'),
    path('coders/', render_template('base/coders.html'), name='coders'),
    path('diskusi/', render_template('base/forum.html'), name='forum'),
    path('tentang/', render_template('base/tentang.html'), name='tentang'),
]
