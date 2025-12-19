from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TithePayment
from .sms_service import sms_service 
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=TithePayment)
def send_tithe_sms_notification(sender, instance, created, **kwargs):
    """Send SMS using the configured provider"""
    if not getattr(settings, 'SEND_SMS_ENABLED', False):
        return
    
    try:
        phone_number = instance.contact_number
        if not phone_number:
            return
        
        if created:
            message = f"Hello {instance.name.name}, your tithe of Tsh {instance.amount} has been recorded. Thank you!"
            print(message)
        else:
            message = f"Hello {instance.name.name}, your tithe has been updated to Tsh {instance.amount}. Thank you!"
        
        # This line never changes regardless of provider!
        result = sms_service.send_sms(phone_number, message)
        
        if result['success']:
            logger.info(f"SMS sent via {result.get('provider')} to {phone_number}")
        else:
            logger.error(f"SMS failed via {result.get('provider')}: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")