import os
import requests

def send_whatsapp(message):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
        payload = {
            'From': 'whatsapp:+17372508034',
            'To': 'whatsapp:+919303520446',
            'Body': message
        }
        response = requests.post(url, data=payload, auth=(account_sid, auth_token))
        return response
    except Exception as e:
        print(f"WhatsApp Error: {e}")