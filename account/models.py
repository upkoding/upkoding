import uuid
from datetime import timedelta
from django.utils.timezone import now
from django.urls import reverse
from django.db import models, transaction
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
    TIME_ZONES = (
        ('Asia/Jakarta', '(WIB) Waktu Indonesia Barat'),
        ('Asia/Makassar', '(WITA) Waktu Indonesia Tengah'),
        ('Asia/Jayapura', '(WIT) Waktu Indonesia Timur'),
    )
    date_modified = models.DateTimeField(auto_now=True)
    avatar = ImageField(
        upload_to=avatar_path,
        blank=True,
        null=True,
        default=None
    )
    point = models.IntegerField(default=0)
    description = models.TextField(blank=True, default='')
    time_zone = models.CharField(
        max_length=100, choices=TIME_ZONES, default='Asia/Jakarta')

    # to keep track of verified email
    verified_email = models.EmailField(blank=True, default='')

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

    def is_pro_user(self):
        try:
            pro_access = self.pro_access
            return pro_access.is_active()
        except Exception:
            return False

    def is_email_verified(self):
        if not self.email:
            return True
        return self.email.lower() == self.verified_email.lower()

    @staticmethod
    def get_active_staffs(exclude_user=None):
        qs = User.objects.filter(is_active=True, is_staff=True)
        return qs.exclude(pk=exclude_user.pk) if exclude_user else qs


class Link(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='link')
    github = models.URLField(
        'Github', max_length=200, blank=True, default='',
        help_text='Format: https://github.com/upkoding')
    gitlab = models.URLField(
        'GitLab', max_length=200, blank=True, default='',
        help_text='Format: https://gitlab.com/upkoding')
    bitbucket = models.URLField(
        'Bitbucket', max_length=200, blank=True, default='',
        help_text='Format: https://bitbucket.org/upkoding/')
    linkedin = models.URLField(
        'LinkedIn', max_length=200, blank=True, default='',
        help_text='Format: https://www.linkedin.com/in/upkoding/')
    facebook = models.URLField(
        'Facebook', max_length=200, blank=True, default='',
        help_text='Format: https://www.facebook.com/upkoding')
    twitter = models.URLField(
        'Twitter', max_length=200, blank=True, default='',
        help_text='Format: https://twitter.com/upkoding')
    youtube = models.URLField(
        'Youtube', max_length=200, blank=True, default='',
        help_text='Format: https://www.youtube.com/c/upkoding')
    website = models.URLField(
        'Website', max_length=200, blank=True, default='',
        help_text='Format: https://www.upkoding.com')
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
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def is_active(self):
        return self.end is not None and self.end > now()

    def extend_days(self, days):
        rightnow = now()

        if not self.start:
            self.start = rightnow
        if not self.end:
            self.end = rightnow
        # if ended in the past, set end-date relative to now time
        # otherwise extend current end-date
        if self.end < rightnow:
            self.end = rightnow + timedelta(days=days)
        else:
            self.end = self.end + timedelta(days=days)
        self.save()
        # TODO: notify user

    def shorten_days(self, days):
        if self.end < now():
            return
        self.end = self.end - timedelta(days=days)
        self.save()


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
    # 0-9 are status based on user-action
    STATUS_ORDER_PENDING = 0
    STATUS_ORDER_CANCELED = 1
    STATUS_ORDER_GIFTED = 2
    # 10-19 are status based on payment status received from payment processor.
    STATUS_PAYMENT_PENDING = 10
    STATUS_PAYMENT_CANCELED = 11
    STATUS_PAYMENT_PAID = 12
    STATUS_PAYMENT_EXPIRED = 13
    STATUS_PAYMENT_REFUND = 14
    STATUS_PAYMENT_FAILED = 15
    STATUSES = [
        (STATUS_ORDER_PENDING, 'order.pending'),
        (STATUS_ORDER_CANCELED, 'order.canceled'),
        (STATUS_ORDER_GIFTED, 'order.gifted'),
        (STATUS_PAYMENT_PENDING, 'payment.pending'),
        (STATUS_PAYMENT_CANCELED, 'payment.canceled'),
        (STATUS_PAYMENT_PAID, 'payment.paid'),
        (STATUS_PAYMENT_EXPIRED, 'payment.expired'),
        (STATUS_PAYMENT_REFUND, 'payment.refund'),
        (STATUS_PAYMENT_FAILED, 'payment.failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_name = models.CharField(max_length=200)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='purchases')
    pro_access = models.ForeignKey(
        ProAccess, on_delete=models.CASCADE, related_name='purchases')
    days = models.IntegerField()
    price = models.IntegerField()
    valid_until = models.DateTimeField(default=valid_until_time)
    status = models.SmallIntegerField(
        default=STATUS_ORDER_PENDING, choices=STATUSES)
    review_required = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['created'],
                         name='purchase_created_idx'),
            models.Index(fields=['status'],
                         name='purchase_status_idx'),
            models.Index(fields=['valid_until'],
                         name='purchase_valid_until_idx'),
            models.Index(fields=['review_required'],
                         name='purchase_review_required_idx'),
        ]

    @property
    def status_label(self):
        if self.status != self.STATUS_ORDER_PENDING or (self.valid_until > now()):
            return self.get_status_display()
        return 'order.expired'

    @property
    def status_color(self):
        """Bootstrap color code"""
        if self.status == self.STATUS_ORDER_PENDING:
            if self.valid_until < now():
                return 'secondary'
            return 'warning'
        if self.status == self.STATUS_ORDER_GIFTED:
            return 'primary'
        if self.status == self.STATUS_PAYMENT_PENDING:
            return 'warning'
        if self.status == self.STATUS_PAYMENT_PAID:
            return 'success'
        if self.status == self.STATUS_PAYMENT_REFUND:
            return 'info'
        if self.status == self.STATUS_PAYMENT_FAILED:
            return 'danger'
        return 'secondary'

    def can_pay(self):
        return self.status == self.STATUS_ORDER_PENDING and self.valid_until > now()

    def is_payment_pending(self):
        return self.status == self.STATUS_PAYMENT_PENDING

    @staticmethod
    def safe_get(id: str):
        try:
            return ProAccessPurchase.objects.get(pk=id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def can_create(user: User):
        """
        A check whether user can create new ProAccessPurchase.
        Eligible users:
        - Users who doesn't have pending ProAccessPurchase. 
        """
        valid_and_pending_purchases = ProAccessPurchase.objects.filter(
            user=user,
            status=ProAccessPurchase.STATUS_ORDER_PENDING,
            valid_until__gte=now()
        )
        if len(valid_and_pending_purchases) > 0:
            return False
        return True

    def set_canceled(self):
        self.status = self.STATUS_ORDER_CANCELED
        self.save()

    def set_gifted(self):
        with transaction.atomic():
            self.status = ProAccessPurchase.STATUS_ORDER_GIFTED
            self.pro_access.extend_days(self.days)
            self.save()


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
    status_code = models.IntegerField()
    gross_amount = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.created.strftime('%Y-%m-%d %H:%M:%S')

    def is_payment_success(self):
        """
        Based on:
        https://docs.midtrans.com/en/after-payment/http-notification?id=best-practice-to-handle-notification
        """
        if self.fraud_status:
            return (self.status_code == 200) and (self.fraud_status == 'accept') and (self.transaction_status in ['settlement', 'capture'])
        return (self.status_code == 200) and (self.transaction_status in ['settlement', 'capture'])

    @staticmethod
    def create_from_payload(payload: dict):
        """
        Only use this method on verified and trusted payload.
        """
        with transaction.atomic():
            payment_type = payload.get('payment_type')
            transaction_id = payload.get('transaction_id')
            transaction_status = payload.get('transaction_status')
            fraud_status = payload.get('fraud_status')
            status_code = int(payload.get('status_code'))
            gross_amount = float(payload.get('gross_amount', '0'))
            order_id = payload.get('order_id')
            purchase = ProAccessPurchase.safe_get(order_id)

            payment_notification = MidtransPaymentNotification(
                purchase=purchase,
                payment_type=payment_type,
                transaction_id=transaction_id,
                transaction_status=transaction_status,
                fraud_status=fraud_status,
                status_code=status_code,
                gross_amount=gross_amount,
                payload=payload
            )
            payment_notification.save()

            if purchase:
                if payment_notification.is_payment_success():
                    purchase.status = ProAccessPurchase.STATUS_PAYMENT_PAID
                    purchase.pro_access.extend_days(purchase.days)
                    purchase.save()
                elif transaction_status == 'expire':
                    purchase.status = ProAccessPurchase.STATUS_PAYMENT_EXPIRED
                    purchase.save()
                elif transaction_status in ['refund', 'partial_refund']:
                    purchase.status = ProAccessPurchase.STATUS_PAYMENT_REFUND
                    purchase.save()
                elif transaction_status in ['pending', 'cancel', 'deny']:
                    # IF if cancel, deny or pending after transaction status was paid (rare case)
                    # THEN set puchase review_required=True
                    if purchase.status == ProAccessPurchase.STATUS_PAYMENT_PAID:
                        purchase.review_required = True
                    else:
                        if transaction_status == 'pending':
                            purchase.status = ProAccessPurchase.STATUS_PAYMENT_PENDING
                        if transaction_status == 'deny':
                            purchase.status = ProAccessPurchase.STATUS_PAYMENT_FAILED
                        if transaction_status == 'cancel':
                            purchase.status = ProAccessPurchase.STATUS_PAYMENT_CANCELED
                    purchase.save()
                else:
                    purchase.review_required = True
                    purchase.save()
