from django.conf import settings
from .sms_api.africastalking import AfricaTalkingProvider
from .sms_api.BeemAfrica import BeemAfrica

class SMSService:
    def __init__(self):
        self.provider = BeemAfrica(
            api_key=settings.BEEM_API_KEY,
            secret_key=settings.BEEM_SECRET_KEY,
            sender_name=getattr(settings, 'BEEM_AFRICA_SENDER_NAME', 'INFO')
        )
    
    def send_sms(self, phone_number, message):
        return self.provider.send_sms(phone_number, message)

# Global instance
sms_service = SMSService()