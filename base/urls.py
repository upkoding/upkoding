from django.urls import path

from .views import render_template, Index

app_name = 'base'


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('tentang/', render_template('base/tentang.html'), name='tentang'),
    path('pro/', render_template('base/pro.html'), name='pro'),
    path('robots.txt', render_template('base/robots.txt', 'text/plain')),
]
