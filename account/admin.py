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


@admin.register(UserSetting)
class UserSettingAdmin(admin.ModelAdmin):
    pass


class MidtransPaymentNotificationInlineAdmin(admin.StackedInline):
    model = MidtransPaymentNotification


@admin.register(ProAccessPurchase)
class ProAccessPurchaseAdmin(admin.ModelAdmin):
    inlines = [MidtransPaymentNotificationInlineAdmin]
    list_display = ['pk', 'user', 'days', 'price', 'valid_until',
                    'status', 'review_required', 'created', 'updated']
    list_filter = ['review_required', 'status']
    actions = ['set_gifted', 'set_reviewed']

    def set_gifted(self, request, queryset):
        if request.user.is_superuser:
            count = 0
            for purchase in queryset:
                purchase.set_gifted()
                count += 1
            self.message_user(
                request, f'{count} purchase(s) marked as gifted.')
    set_gifted.short_description = 'Berikan Pro Access gratis'

    def set_reviewed(self, request, queryset):
        if request.user.is_superuser:
            rows_updated = queryset.update(review_required=False)
            self.message_user(
                request, f'{rows_updated} purchase(s) marked as reviewed.')
    set_reviewed.short_description = 'Tandai sudah direview'


class ProAccessPurchaseInlineAdmin(admin.StackedInline):
    model = ProAccessPurchase


@admin.register(ProAccess)
class ProAccessAdmin(admin.ModelAdmin):
    inlines = [ProAccessPurchaseInlineAdmin]
    list_display = ['user', 'start', 'end', 'created', 'updated']


class ProAccessInlineAdmin(admin.StackedInline):
    model = ProAccess


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [ProAccessInlineAdmin, LinkInlineAdmin]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
         'fields': ('first_name', 'email', 'verified_email', 'point', 'description', 'time_zone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
