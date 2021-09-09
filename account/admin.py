from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    User,
    Link,
    UserSetting,
    ProAccess,
    ProAccessPurchase,
    MidtransPaymentNotification
)


class LinkInlineAdmin(admin.StackedInline):
    model = Link


class UserSettingAdmin(admin.ModelAdmin):
    model = UserSetting


class MidtransPaymentNotificationInlineAdmin(admin.StackedInline):
    model = MidtransPaymentNotification


class ProAccessPurchaseAdmin(admin.ModelAdmin):
    model = ProAccessPurchase
    inlines = [MidtransPaymentNotificationInlineAdmin]
    list_display = ['pk', 'user', 'days', 'price', 'valid_until',
                    'status', 'review_required', 'created', 'updated']
    list_filter = ['review_required', 'status']


class ProAccessPurchaseInlineAdmin(admin.StackedInline):
    model = ProAccessPurchase


class ProAccessAdmin(admin.ModelAdmin):
    model = ProAccess
    inlines = [ProAccessPurchaseInlineAdmin]
    list_display = ['user', 'start', 'end', 'created', 'updated']


class ProAccessInlineAdmin(admin.StackedInline):
    model = ProAccess


class CustomUserAdmin(UserAdmin):
    inlines = [ProAccessInlineAdmin, LinkInlineAdmin]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
         'fields': ('first_name', 'email', 'point', 'description')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserSetting, UserSettingAdmin)
admin.site.register(ProAccess, ProAccessAdmin)
admin.site.register(ProAccessPurchase, ProAccessPurchaseAdmin)
