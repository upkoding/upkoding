from django.http import HttpRequest
from django.conf import settings


def upkoding(request: HttpRequest):
    """
    Add custom values to context.
    """
    return {
        'domain': settings.SITE_DOMAIN,
        'ga_tracking_id': settings.GOOGLE_ANALYTICS_TRACKING_ID,
    }
