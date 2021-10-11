from django.conf import settings

APPLICATION_ID = getattr(settings, 'DISCORD_APPLICATION_ID', '896220464123359272')
PUBLIC_KEY = getattr(settings,'DISCORD_PUBLIC_KEY', '4c3242976fde0839460093c083959fae1d001bb9c5f5cefee326d0f12faeedb0')
BOT_TOKEN = getattr(settings, 'DISCORD_BOT_TOKEN', 'ODk2MjIwNDY0MTIzMzU5Mjcy.YWD8WQ.Y3wHcehwMguTU5G_MLjLjQIvf9g')