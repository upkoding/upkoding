import hashlib
import midtransclient
from django.conf import settings

snap = midtransclient.Snap(
    is_production=settings.MIDTRANS_IS_PRODUCTION,
    server_key=settings.MIDTRANS_SERVER_KEY,
    client_key=settings.MIDTRANS_CLIENT_KEY
)


def get_redirect_url(
        order_id: str,
        order_name: str,
        gross_amount: int,
        customer_first_name: str,
        customer_last_name: str,
        customer_email: str) -> str:

    param = {
        'transaction_details': {
            'order_id': order_id,
            'gross_amount': gross_amount
        },
        'item_details': [{
            'id': order_id,
            'price': gross_amount,
            'quantity': 1,
            'name': order_name,
            'brand': 'UpKoding',
            'merchant_name': 'UpKoding'
        }],
        'customer_details': {
            'first_name': customer_first_name,
            'last_name': customer_last_name,
            'email': customer_email
        },
    }

    transaction = snap.create_transaction(param)
    return transaction['redirect_url']


def is_payment_notification_valid(merchant_id: str, payload: dict):
    """
    Based on: https://docs.midtrans.com/en/after-payment/http-notification?id=verifying-notification-authenticity

    SHA512(order_id+status_code+gross_amount+ServerKey)
    """
    if merchant_id != settings.MIDTRANS_MERCHANT_ID:
        return False
        
    signature = payload.get('signature_key')
    order_id = payload.get('order_id')
    status_code = payload.get('status_code')
    gross_amount = payload.get('gross_amount')
    raw_signature = f'{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}' \
        .encode('utf-8')
    return hashlib.sha512(raw_signature).hexdigest() == signature
