from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TithePayment
from .sms_service import sms_service 
import logging
import re

logger = logging.getLogger(__name__)

def format_phone_number(phone):
    """Ensures number is in 255XXXXXXXXX format for Beem/Africa's Talking"""
    cleaned = re.sub(r'\D', '', str(phone))  # Remove non-digits
    if cleaned.startswith('0'):
        return '255' + cleaned[1:]
    if cleaned.startswith('+'):
        return cleaned[1:]
    return cleaned

@receiver(post_save, sender=TithePayment)
def send_tithe_sms_notification(sender, instance, created, **kwargs):
    # 1. Check if feature is enabled
    if not getattr(settings, 'SEND_SMS_ENABLED', False):
        return # Just exit; return value is ignored by Django signals

    try:
        # 2. Validate and Format Phone
        raw_phone = getattr(instance, 'contact_number', None)
        if not raw_phone:
            logger.warning(f"No phone number for Tithe ID {instance.id}")
            return
        
        phone_number = format_phone_number(raw_phone)
        
        # 3. Construct Message
        # Accessing instance.name.name assumes a Foreign Key to a Member model
        member_name = instance.name.name if hasattr(instance.name, 'name') else "Member"
        
        if created:
            message = f"Habari {member_name}, zaka yako ya Tsh {instance.amount:,} imepokelewa. Asante!"
        else:
            # Only send on update if specifically required to avoid spamming users
            message = f"Habari {member_name}, taarifa za zaka yako zimepata mabadiliko kuwa Tsh {instance.amount:,}. Asante!"
        
        # 4. Execute Send
        # Note: In 2026, consider: my_task.delay(phone_number, message) for Celery
        result = sms_service.send_sms(phone_number, message)
        
        if result.get('success'):
            logger.info(f"SMS SUCCESS: ID {instance.id} via {result.get('provider')}")
        else:
            logger.error(f"SMS FAILURE: ID {instance.id} | Error: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"CRITICAL SMS ERROR: {str(e)}", exc_info=True)
