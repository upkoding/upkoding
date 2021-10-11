import requests
from django.core.management.base import BaseCommand, CommandError

from discord.conf import APPLICATION_ID, BOT_TOKEN

url = f'https://discord.com/api/v8/applications/{APPLICATION_ID}/commands'


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
        headers = {
            'Authorization': f'Bot {BOT_TOKEN}'
        }
        for cmd in commands:
            name = cmd.get('name')
            try:
                requests.post(url, headers=headers, json=cmd)
                self.stdout.write(self.style.SUCCESS(
                    f'Command `{name}` registered.'))
            except Exception as e:
                raise CommandError(
                    f'Error registering `{name}` command. Err: {e}')
