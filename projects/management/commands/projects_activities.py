from django.core.management.base import BaseCommand, CommandError

from projects.models import UserProjectEvent
from projects.notifications import UserProjectEventNotification, delete_activity


class Command(BaseCommand):
    help = 'Sync existing projects activities to getstream.io'

    def add_arguments(self, parser):
        parser.add_argument('--sync', action='store_true',
                            help='Sync all activities')
        parser.add_argument('--delete', action='store_true',
                            help='Delete all activities')
        parser.add_argument('--dry', action='store_true',
                            help='Run simulation (not executing real action)')

    def handle(self, *args, **options):
        is_dry = options.get('dry')
        if options['sync']:
            self.sync(is_dry)
        elif options['delete']:
            self.delete(is_dry)

    def sync(self, dry):
        event_types = [
            UserProjectEvent.TYPE_PROJECT_START,
            UserProjectEvent.TYPE_PROJECT_COMPLETE,
            UserProjectEvent.TYPE_PROJECT_INCOMPLETE,
            UserProjectEvent.TYPE_REVIEW_MESSAGE,
            UserProjectEvent.TYPE_REVIEW_REQUEST,
        ]
        events = UserProjectEvent.objects.filter(
            event_type__in=event_types)
        total_count = len(events)
        success_count = 0
        for event in events:
            try:
                if not dry:
                    UserProjectEventNotification(event=event, is_sync=True)
                self.stdout.write(self.style.SUCCESS(
                    f'[OK] Event {event.pk} synced'))
                success_count += 1
            except Exception as e:
                raise CommandError(
                    f'[ERR] Event {event.pk} not synced. Err: {e}')

        self.stdout.write(self.style.WARNING(
            f'Finish! {success_count} out of {total_count} event(s) successfully synced.'))

    def delete(self, dry):
        event_types = [
            UserProjectEvent.TYPE_PROJECT_START,
            UserProjectEvent.TYPE_PROJECT_COMPLETE,
            UserProjectEvent.TYPE_PROJECT_INCOMPLETE,
            UserProjectEvent.TYPE_REVIEW_MESSAGE,
            UserProjectEvent.TYPE_REVIEW_REQUEST,
        ]
        events = UserProjectEvent.objects.filter(
            event_type__in=event_types)
        total_count = len(events)
        success_count = 0
        for event in events:
            try:
                if not dry:
                    delete_activity(event)
                self.stdout.write(self.style.SUCCESS(
                    f'[OK] Activity {event.pk} deleted'))
                success_count += 1
            except Exception as e:
                raise CommandError(
                    f'[ERR] Activity {event.pk} not deleted. Err: {e}')

        self.stdout.write(self.style.WARNING(
            f'Finish! {success_count} out of {total_count} activities(s) successfully deleted.'))
