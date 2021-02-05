from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib import messages


def login(request):
    return render(request, 'account/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'Sampai jumpa di lain kesempatan :)',
                  extra_tags='success')
    return HttpResponseRedirect(reverse('account:login'))


def profile(request):
    return render(request, 'account/profile.html', {'tab': 'profile'})


def authentication(request):
    return render(request, 'account/profile.html', {'tab': 'auth'})


def settings(request):
    return render(request, 'account/profile.html', {'tab': 'settings'})
