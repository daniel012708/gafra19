from twilio.rest import Client
from django.conf import settings

def enviar_whatsapp(mensaje):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_='whatsapp:+14155238886',
        to=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
        body=mensaje
    )