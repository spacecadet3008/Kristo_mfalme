import africastalking
from ..base import BaseSMSProvider

class AfricaTalkingProvider(BaseSMSProvider):
    def __init__(self, username, api_key, sender_id=None):
        africastalking.initialize(username, api_key)
        self.sms = africastalking.SMS
        self.sender_id = sender_id
    
    def send_sms(self, phone_number, message):
        try:
            params = {'to': [phone_number], 'message': message}
            if self.sender_id:
                params['from_'] = self.sender_id
                
            response = self.sms.send(**params)
            
            if response['SMSMessageData']['Recipients']:
                recipient = response['SMSMessageData']['Recipients'][0]
                return {
                    'success': recipient['status'] == 'Success',
                    'message_id': recipient.get('messageId'),
                    'data': response,
                    'provider': 'africastalking'
                }
            return {'success': False, 'error': 'No recipients'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'provider': 'africastalking'}