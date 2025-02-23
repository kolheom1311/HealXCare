from twilio.rest import Client
from django.conf import settings

def send_otp(phone_number, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message_body = (
        "\n\n💙 Welcome to HealXCare! 💙\n\n"
        f"Your secure OTP for verification is: {otp}.\n\n"
        "🔒 For your security, NEVER share this code with anyone.\n"
        "⏳ This OTP is valid for 5 minutes only.\n\n"
        "Need help? Contact our support team anytime!\n"
        "Stay safe and healthy,\n"
        "✨ Team HealXCare ✨"
    )

    message = client.messages.create(
        # body=f"Your OTP is {otp}. Do not share it with anyone.",
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid
