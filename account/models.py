import uuid
from datetime import timedelta
from django.utils.timezone import now
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.humanize.templatetags import humanize
from django.conf import settings

from sorl.thumbnail import ImageField, get_thumbnail
from .managers import UserSettingManager, USER_SETTING_TYPES, USER_SETTING_TYPE_BOOL


def avatar_path(instance, filename):
    """
    Custom avatar path: avatar/u123-12345678.png
    """
    return 'avatar/u{}-{}.{}'.format(
        instance.id,
        int(instance.date_joined.timestamp()),
        filename.split('.')[-1]
    )


class User(AbstractUser):
    date_modified = models.DateTimeField(auto_now=True)
    avatar = ImageField(
        upload_to=avatar_path,
        blank=True,
        null=True,
        default=None
    )
    point = models.IntegerField(default=0)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-point']

    def avatar_url(self, size=100):
        """
        If user upload their picture manually, use it. Otherwise generate from default Gravatar image.
        """
        if self.avatar:
            return get_thumbnail(self.avatar, '{}x{}'.format(size, size), crop='center', quality=99).url
        return 'https://www.gravatar.com/avatar/{}?d=retro&f=y&s={}'.format(self.id, size)

    def get_absolute_url(self):
        return reverse('coders:detail', args=[self.username])

    def get_display_name(self):
        return self.username if not self.first_name else self.first_name

    def get_point_display(self):
        return '{}{}'.format(humanize.intcomma(self.point), settings.POINT_UNIT)

    def get_link(self):
        try:
            return self.link
        except ObjectDoesNotExist:
            return None

    def add_point(self, point):
        self.point = models.F('point') + point
        self.save()

    def remove_point(self, point):
        self.point = models.F('point') - point
        self.save()


class Link(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='link')
    github = models.CharField(
        'Github', max_length=200, blank=True, default='')
    gitlab = models.CharField(
        'GitLab', max_length=200, blank=True, default='')
    bitbucket = models.CharField(
        'Bitbucket', max_length=200, blank=True, default='')
    linkedin = models.CharField(
        'LinkedIn', max_length=200, blank=True, default='')
    facebook = models.CharField(
        'Facebook', max_length=200, blank=True, default='')
    twitter = models.CharField(
        'Twitter', max_length=200, blank=True, default='')
    youtube = models.CharField(
        'Youtube', max_length=200, blank=True, default='')
    website = models.CharField(
        'Website', max_length=200, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Links: {}".format(self.user.username)


class UserSetting(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_settings')
    key = models.CharField(max_length=64, db_index=True)
    value = models.CharField(max_length=200, blank=True, default='true')
    type = models.SmallIntegerField(
        default=USER_SETTING_TYPE_BOOL,
        choices=USER_SETTING_TYPES)

    objects = UserSettingManager()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'key', 'type'],
                         name='user_setting_key_type_idx'),
        ]

        constraints = [
            # to make sure there's only one UserSetting record with the same `user` and `key`
            models.UniqueConstraint(
                fields=['user', 'key', 'type'],
                name='unique_user_setting_key_type')
        ]

    def __str__(self):
        return '[{}] {}:{}'.format(self.user.pk, self.key, self.value)


class ProAccess(models.Model):
    """
    To keep track of user's PRO access lifetime.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='pro_access')
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


def valid_until_time():
    """
    Once user purchase an access, the purchase will be valid for limited amount of time.
    Once invalid, user will unable to make payment on that specific purchase and need to create the new one.
    """
    return now() + timedelta(days=3)


class ProAccessPurchase(models.Model):
    """
    User could purchase an access or extend their access lifetime anytime.
    A purchase valid for limited amount of time eg. 3 days and they need to
    make payment during this time.
    """
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_365 = 365
    DAYS_CHOICES = [
        (DAYS_30, '1 bulan (30 hari)'),
        (DAYS_90, '3 bulan (90 hari)'),
        (DAYS_365, '1 tahun (365 hari)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='purchases')
    pro_access = models.ForeignKey(
        ProAccess, on_delete=models.CASCADE, related_name='purchases')
    days = models.IntegerField(choices=DAYS_CHOICES)
    price = models.IntegerField()
    valid_until = models.DateTimeField(default=valid_until_time)
    paid_at = models.DateTimeField(blank=True, null=True)
    gifted_at = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @staticmethod
    def safe_get(id: str):
        try:
            return ProAccessPurchase.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None


class MidtransPaymentNotification(models.Model):
    """
    Store history of payment notification received from Midtrans.
    https://docs.midtrans.com/en/after-payment/http-notification
    """
    # a reference to ProAccessPurchase, allow null in case order_id (ProAccessPurchase) not found.
    purchase = models.ForeignKey(
        ProAccessPurchase,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    # original raw JSON payload from notification
    payload = models.JSONField(blank=True, null=True)
    payment_type = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=200)
    transaction_status = models.CharField(max_length=50)
    fraud_status = models.CharField(max_length=50, blank=True, null=True)
    gross_amount = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @staticmethod
    def create_from_payload(payload: dict):
        """
        Only use this method on verified and trusted payload.
        """
        payment_type = payload.get('payment_type')
        transaction_id = payload.get('transaction_id')
        transaction_status = payload.get('transaction_status')
        fraud_status = payload.get('fraud_status')
        gross_amount = float(payload.get('gross_amount', '0'))

        order_id = payload.get('order_id')
        purchase = ProAccessPurchase.safe_get(order_id)

        payment_notification = MidtransPaymentNotification(
            purchase=purchase,
            payment_type=payment_type,
            transaction_id=transaction_id,
            transaction_status=transaction_status,
            fraud_status=fraud_status,
            gross_amount=gross_amount,
            payload=payload
        )
        payment_notification.save()
