# sms/providers/nextsms.py
import requests
from typing import Dict, Any
from ..base import BaseSMSProvider

class NextSMSProvider(BaseSMSProvider):
    def __init__(self, api_key: str, api_secret: str, sender_id: str, base_url: str = "https://apigw.nextsms.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.sender_id = sender_id
        self.base_url = base_url
    
    def _get_auth_header(self):
        return {
            'Authorization': f'Bearer {self.api_key}:{self.api_secret}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/sms/v1/text/single"
        
        payload = {
            "from": self.sender_id,
            "to": self._clean_phone_number(phone_number),
            "text": message
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_auth_header(), timeout=30)
            response_data = response.json()
            
            return {
                'success': response.status_code == 200,
                'message_id': response_data.get('messageId'),
                'data': response_data,
                'status_code': response.status_code,
                'provider': 'nextsms'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'nextsms'
            }
    
    def send_bulk_sms(self, recipients: list) -> Dict[str, Any]:
        # Implementation for bulk SMS
        pass
    
    def get_balance(self) -> Dict[str, Any]:
        # Implementation for balance check
        pass
    
    def _clean_phone_number(self, phone_number: str) -> str:
        cleaned = ''.join(filter(str.isdigit, str(phone_number)))
        if cleaned.startswith('0'):
            cleaned = '255' + cleaned[1:]
        return cleaned