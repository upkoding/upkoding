import hashlib
import urllib
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.core.exceptions import ValidationError

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

    def avatar_url(self, size=100):
        """
        If user upload their picture manually, use it. Otherwise generate from default Gravatar image.
        """
        if self.avatar:
            return get_thumbnail(self.avatar, '{}x{}'.format(size, size), crop='center', quality=99).url
        return 'https://www.gravatar.com/avatar/{}?d=retro&f=y&s={}'.format(self.id, size)
