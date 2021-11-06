from django.http import HttpRequest
from django.conf import settings
from upkoding import pricing


def upkoding(request: HttpRequest):
    """
    Add custom values to context.
    """
    return {
        'app_version': settings.APP_VERSION,
        'domain': settings.SITE_DOMAIN,
        'ga_tracking_id': settings.GOOGLE_ANALYTICS_TRACKING_ID,
        'statuspage_url': settings.STATUSPAGE_URL,
        'plans': pricing.plans,
        'show_roadmaps': settings.SHOW_ROADMAPS,
    }
