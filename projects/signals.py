from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProject, UserProjectEvent


# @receiver(post_save, sender=UserProject, dispatch_uid='user_project_event')
# def create_user_project_event(sender, instance, created, **kwargs):
#     if created:
#         print('Project started')
#     else:
#         print(instance.requirements)
#         print(instance._original_values.get('requirements'))
