import hashlib
import urllib
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static


class User(AbstractUser):

    def avatar_url(self, size=40):
        """
        If user upload their picture manually, use it. Otherwise generate Gravatar URL.
        """
        return "https://www.gravatar.com/avatar/%s?%s" % (
            hashlib.md5(self.email.lower().encode('utf-8')).hexdigest(),
            urllib.parse.urlencode({'d': 'retro', 's': str(size)})
        )
