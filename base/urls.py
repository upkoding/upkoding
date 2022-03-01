from django.urls import path

from .views import render_template, Index, Contributors

app_name = 'base'


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('classrooms/', render_template('base/classrooms.html'), name='classrooms'),
    path('tentang/', render_template('base/tentang.html'), name='tentang'),
    path('aturan-dan-privasi/', render_template('base/tos.html'), name='tos'),
    path('pro/', render_template('base/pro.html'), name='pro'),
    path('kontributor/', Contributors.as_view(), name='contributors'),
    path('robots.txt', render_template('base/robots.txt', 'text/plain'))
]
