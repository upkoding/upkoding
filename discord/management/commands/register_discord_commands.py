import requests
from django.core.management.base import BaseCommand, CommandError

from discord.conf import COMMANDS_API_URL, BOT_REQUEST_HEADERS

commands = [
    {
        'name': 'verifikasi',
        'type': 1,  # CHAT_INPUT
        'description': 'Verifikasi dengan akun upkoding.com untuk mengakses Discord secara penuh.',
        'options': [
            {
                'name': 'token',
                'description': 'Token verifikasi Discord dari upkoding.com',
                'type': 3,  # STRING
                'required': True
            }
        ]
    }
]


class Command(BaseCommand):
    help = 'Register all Discord commands'

    def handle(self, *args, **options):
        for cmd in commands:
            name = cmd.get('name')
            try:
                resp = requests.post(COMMANDS_API_URL,
                                     headers=BOT_REQUEST_HEADERS, json=cmd)
                resp.raise_for_status()
                self.stdout.write(self.style.SUCCESS(
                    f'Command `{name}` registered.'))
            except Exception as e:
                raise CommandError(
                    f'Error registering `{name}` command. Err: {e}')
