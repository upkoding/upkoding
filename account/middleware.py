import six
from django.conf import settings
from django.shortcuts import redirect, reverse
from django.contrib import messages

from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import NotAllowedToDisconnect, SocialAuthBaseException


class SocialLoginExceptionMiddleware(SocialAuthExceptionMiddleware):
    """
    Overrides default exception middleware so we can redirect user to correct page when error happened
    and display correct message.
    """

    def process_exception(self, request, exception):
        strategy = getattr(request, 'social_strategy', None)
        if strategy is None or self.raise_exception(request, exception):
            return

        if isinstance(exception, SocialAuthBaseException):
            backend = getattr(request, 'backend', None)
            backend_name = getattr(backend, 'name', 'unknown-backend')

            message = six.text_type(exception)
            if isinstance(exception, NotAllowedToDisconnect):
                message = 'Tidak bisa di disconnect karena {} satu-satunya metode login saat ini.'.format(
                    backend_name)
            messages.info(request, message, extra_tags='danger')

            if request.user.is_authenticated:
                return redirect(reverse('account:settings'))
            return redirect(settings.LOGIN_ERROR_URL)
