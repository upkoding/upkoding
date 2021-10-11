import json
import logging
from discord_interactions import InteractionResponseType
from account.models import User, UserSetting

log = logging.getLogger(__name__)


def verifikasi(command, data):
    """
    Verify user's Discord token.
    Only process interaction from DM message.
    """
    discord_user = data.get('user')
    discord_member = data.get('member')
    # if interaction made from channel, throw error.
    if discord_member:
        raise Exception('Jangan verifikasi akun di channel, DM saya langsung!')

    # read command options
    options = command.get('options')
    upkoding_token = None
    for option in options:
        if option['name'] == 'token':
            upkoding_token = option['value']

    tokens = upkoding_token.split('@')
    if len(tokens) != 2:
        raise Exception('Gagal! Format token tidak valid.')

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

        # verified
        # TODO: upgrade discord user role.
        verified_status = {
            'verified': True,
            'user': discord_user
        }
        UserSetting.objects.discord_access_token_status(
            user, json.dumps(verified_status))
    except Exception as e:
        log.warning(e)
        raise Exception(
            'Gagal! Token tidak valid atau sudah pernah digunakan.')

    return {
        'type': InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        'data': {
            'content': 'Akun terverifikasi! selamat datang di Discord UpKoding.'
        }
    }
