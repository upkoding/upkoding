from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib import messages


def signin(request):
    return render(request, 'account/login.html')


def signout(request):
    logout(request)
    messages.info(request, 'Sampai jumpa di lain kesempatan :)',
                  extra_tags='success')
    return HttpResponseRedirect(reverse('account:login'))


def profile(request):
    return render(request, 'account/profile.html')
