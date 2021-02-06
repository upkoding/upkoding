from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

app_name = 'website'


def render_template(name):
    return TemplateView.as_view(template_name=name)


urlpatterns = [
    path('', render_template('website/index.html'), name='index'),
    path('proyek/', render_template('website/proyek.html'), name='proyek'),
    path('coders/', render_template('website/coders.html'), name='coders'),
    path('diskusi/', render_template('website/forum.html'), name='forum'),
    path('tentang/', render_template('website/tentang.html'), name='tentang'),
]
