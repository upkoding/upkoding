"""upkoding URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path, include
from django.contrib.staticfiles.urls import static


def appengine_warmup(request):
    return HttpResponse('ok')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls', namespace='account')),
    path('proyek/', include('projects.urls', namespace='projects')),
    path('coders/', include('coders.urls', namespace='coders')),
    path('_ah/warmup/', appengine_warmup),
    path('', include('base.urls', namespace='base')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
