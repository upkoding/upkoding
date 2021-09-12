from django.contrib.auth.views import LogoutView
from django.urls import path, include

from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileFormView.as_view(), name='profile'),
    path('auths/', views.AuthenticationMethodFormView.as_view(), name='auths'),
    path('links/', views.LinksFormView.as_view(), name='links'),
    path('notifications/', views.NotificationFormView.as_view(), name='notifications'),
    path('pro/', views.ProStatusView.as_view(), name='pro'),
    path('pro/purchases/cancel/',
         views.purchase_cancel, name='pro_purchase_cancel'),
    path('pro/purchases/payment/',
         views.purchase_payment, name='pro_purchase_payment'),
    path('midtrans/payment_notification/',
         views.midtrans_payment_notification, name='midtrans_payment_notification'),
    # complete namespace: account:social
    path('', include('social_django.urls', namespace='social')),
    path('', views.IndexView.as_view(), name='index'),
]
