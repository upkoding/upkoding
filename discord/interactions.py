import json
import logging
import requests
from django.utils.timezone import now
from discord_interactions import InteractionResponseType
from account.models import User, UserSetting
from discord.conf import API_BASE_URL, GUILD_ID, UPKODERS_ROLE_ID, BOT_REQUEST_HEADERS

log = logging.getLogger(__name__)


def set_user_role(user_id, role_id):
    set_role_url = f'{API_BASE_URL}/guilds/{GUILD_ID}/members/{user_id}/roles/{role_id}'
    resp = requests.put(url=set_role_url, headers=BOT_REQUEST_HEADERS)
    resp.raise_for_status()
    return resp


def delete_message(channel_id, message_id):
    delete_message_url = f'{API_BASE_URL}/channels/{channel_id}/messages/{message_id}'
    resp = requests.delete(url=delete_message_url, headers=BOT_REQUEST_HEADERS)
    resp.raise_for_status()
    return resp


def verifikasi(command, data):
    """
    Verify user's Discord token.
    Only process interaction from DM message.
    """
    discord_user = data.get('user')
    discord_member = data.get('member')

    # if interaction made from channel, delete the message and throw error.
    if discord_member:
        raise Exception(
            'Jangan verifikasi akun di channel, DM saya langsung! (Token verifikasi adalah rahasia, tolong hapus pesan ini).')

    # read command options
    options = command.get('options')
    upkoding_token = None
    for option in options:
        if option['name'] == 'token':
            upkoding_token = option['value']

    tokens = upkoding_token.split('@')
    if len(tokens) != 2:
        raise Exception('Verifikasi gagal! Format token tidak valid.')

    username, token = tokens
    try:
        user = User.objects.get(username=username)
        
        # check token
        user_saved_token = UserSetting.objects.get_setting(
            user=user, key='discord_access_token')
        if token != user_saved_token:
            raise Exception('token_invalid')

        # check status
        user_saved_token_status = UserSetting.objects.get_setting(
            user=user, key='discord_access_token_status', default=json.dumps(dict()))
        status = json.loads(user_saved_token_status)
        if status.get('verified'):
            raise Exception('token_already_verified')

        # upgrade roles
        discord_user_id = discord_user.get('id')
        set_user_role(discord_user_id, UPKODERS_ROLE_ID)

        # update token status
        verified_status = {
            'verified': True,
            'timestamp': int(now().timestamp()),
            'discord_user': {
                'id': discord_user_id,
                'username': discord_user.get('username')
            }
        }
        UserSetting.objects.discord_access_token_status(
            user, json.dumps(verified_status))
    except Exception as e:
        log.warning(e)
        raise Exception(
            'Verifikasi gagal! Token tidak valid atau sudah pernah digunakan.')

    return {
        'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        'data': {
            'content': 'Akun terverifikasi! selamat datang di Discord UpKoding.'
        }
    }
