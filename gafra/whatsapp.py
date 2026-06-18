from django.conf import settings

try:
    from twilio.rest import Client
except Exception:
    Client = None


def enviar_whatsapp(mensaje):
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '')

    if not Client or not account_sid or not auth_token or not whatsapp_number:
        return False

    client = Client(account_sid, auth_token)
    client.messages.create(
        from_='whatsapp:+14155238886',
        to=f'whatsapp:{whatsapp_number}',
        body=mensaje,
    )
    return True