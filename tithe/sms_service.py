from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms(phone_number, message):
    # FIXED: Shortened to meet 11-character Alphanumeric Sender ID limits
    sender_name = getattr(settings, 'BEEM_SENDER_NAME', "BEEM")
    
    # 2026 Best Practice: Add a prefix to the message for clarity in mock mode
    formatted_message = f"[{sender_name}] {message}"
    
    # Structured logging for easier debugging in 2026
    logger.info(
        "SMS MOCK TRANSACTION: To=%s | Sender=%s | Msg=%s | Status=MOCK_SUCCESS",
        phone_number, sender_name, message
    )
    
    return {
        'success': True,
        'message_id': f'mock_{phone_number}_{id(message)}',
        'provider': 'mock',
        'data': {
            'status': 'success',
            'sender': sender_name,
            'body': formatted_message
        }
    }

class SMSService:
    def send_sms(self, phone_number, message):
        # Prevent accidental production use
        if not settings.DEBUG and not getattr(settings, 'ENABLE_MOCK_SMS', False):
            logger.error("Attempted to use Mock SMS in Production environment!")
            return {'success': False, 'error': 'Mock service disabled in production'}
            
        return send_sms(phone_number, message)

sms_service = SMSService()
