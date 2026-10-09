def send_whatsapp(message):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'

    payload = {
        'From': 'whatsapp:+17372508034',
        'To': 'whatsapp:+919303520446',
        'Body': message,
    }

try:
    requests.post(url, data=payload, auth=(account_sid, auth_token))
except Exception as e:
    print(f'WhatsApp Error: {e}')