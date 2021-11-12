from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from social_django.models import UserSocialAuth
from account.models import User


class Command(BaseCommand):
    help = 'Verify user email address'

    def handle(self, *args, **options):
        pages = Paginator(User.objects.all(), per_page=100)
        for p in range(1, pages.num_pages + 1):
            users = pages.page(p)
            for user in users:
                # current email
                current_email = user.email
                user_pk = user.pk

                # auths
                auths = UserSocialAuth.objects.filter(user=user)
                if len(auths) == 1:
                    auth = auths[0]
                    # uid == current email OR uid is not an email <-- mark verified
                    if ('@' in auth.uid and auth.uid == current_email) or (not '@' in auth.uid):
                        user.verified_email = current_email
                        user.save()
                    else:
                        self.stdout.write(self.style.ERROR(
                            f'[{user_pk}] {current_email} not verified'))
                else:
                    verified = False
                    for auth in auths:
                        if auth.uid == current_email:
                            user.verified_email = current_email
                            user.save()
                            verified = True
                            break
                    if verified:
                        verified = False
                    else:
                        self.stdout.write(self.style.ERROR(
                            f'[{user_pk}] {current_email} not verified'))
