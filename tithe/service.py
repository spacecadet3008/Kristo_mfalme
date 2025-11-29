from django.conf import settings
from .sms_api.africastalking import AfricaTalkingProvider

class SMSService:
    def __init__(self):
        self.provider = AfricaTalkingProvider(
            username=settings.AFRICASTALKING_USERNAME,
            api_key=settings.AFRICASTALKING_API_KEY,
            sender_id=getattr(settings, 'AFRICASTALKING_SENDER_ID', None)
        )
    
    def send_sms(self, phone_number, message):
        return self.provider.send_sms(phone_number, message)

# Global instance
sms_service = SMSService()