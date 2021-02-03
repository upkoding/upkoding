from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.messages import add_message


def index(request):
    return render(request, 'website/index.html')


def about(request):
    return render(request, 'website/about.html')


def signin(request):
    return render(request, 'website/signin.html')


def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('website:index'))
