from django.conf import settings

APPLICATION_ID = getattr(settings, 'DISCORD_APPLICATION_ID', None)
PUBLIC_KEY = getattr(settings, 'DISCORD_PUBLIC_KEY', None)
BOT_TOKEN = getattr(settings, 'DISCORD_BOT_TOKEN', None)
GUILD_ID = getattr(settings, 'DISCORD_GUILD_ID', None)
UPKODERS_ROLE_ID = getattr(settings, 'DISCORD_UPKODERS_ROLE_ID', None)

BOT_REQUEST_HEADERS = {
    'Authorization': f'Bot {BOT_TOKEN}'
}

API_BASE_URL = 'https://discord.com/api/v8'
COMMANDS_API_URL = f'{API_BASE_URL}/applications/{APPLICATION_ID}/commands'
