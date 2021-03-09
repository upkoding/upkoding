from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.humanize.templatetags import humanize
from django.conf import settings

from sorl.thumbnail import ImageField, get_thumbnail


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
