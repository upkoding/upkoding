import json
from django.http.response import HttpResponse, JsonResponse
from django.views.generic import View
from discord_interactions import verify_key, InteractionType, InteractionResponseType

from discord.conf import PUBLIC_KEY
from discord import interactions


class InteractionHandler(View):

    def request_is_valid(self, request):
        signature = request.headers.get('X-Signature-Ed25519')
        timestamp = request.headers.get('X-Signature-Timestamp')
        if signature and timestamp and verify_key(request.body, signature, timestamp, PUBLIC_KEY):
            return True
        return False

    def post(self, request):
        is_valid = self.request_is_valid(request)
        if not is_valid:
            return HttpResponse('Bad request signature', status=401)
        data = json.loads(request.body)
        if data.get('type') == InteractionType.PING:
            return JsonResponse({'type': InteractionResponseType.PONG})

        cmd = data.get('data', {})
        cmd_name = cmd.get('name')
        try:
            if cmd_name:
                handler = getattr(interactions, cmd_name, None)
                if not handler:
                    raise Exception('Maaf, perintah tidak ditemukan!')
                return JsonResponse(handler(cmd, data))
            raise Exception('Maaf, perintah tidak valid!')
        except Exception as e:
            return JsonResponse({
                'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                'data': {
                    'content': str(e)
                }
            })
