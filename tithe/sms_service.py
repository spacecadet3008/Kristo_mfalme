from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms(phone_number, message):
    """
    Mock SMS service for development/testing
    """
    sender_name = "KRISTO MFALME"
    
    # Option 1: Add sender name to the beginning of message
    formatted_message = f"{sender_name}: {message}"
    
    # Or Option 2: Add sender name at the end
    # formatted_message = f"{message}\n\n- {sender_name}"
    
    logger.info(f"📱 MOCK SMS SENT:")
    logger.info(f"   From: {sender_name}")
    logger.info(f"   To: {phone_number}")
    logger.info(f"   Message: {formatted_message}")
    logger.info(f"   Status: SUCCESS (Mock)")
    
    # Always return success in development
    return {
        'success': True,
        'message_id': f'mock_{phone_number}_{id(message)}',
        'provider': 'mock',
        'sender': sender_name,
        'data': {
            'status': 'Mocked success for development',
            'from': sender_name,
            'original_message': message,
            'formatted_message': formatted_message
        }
    }

# For backward compatibility with your signals
class SMSService:
    def send_sms(self, phone_number, message):
        return send_sms(phone_number, message)

# Create instance
sms_service = SMSService()