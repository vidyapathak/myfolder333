import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# .env file se variables load karein
load_dotenv()

# 1. India Timezone (IST = UTC + 5:30) set karein
ist_timezone = timezone(timedelta(hours=5, minutes=30))

# --- WhatsApp Function ---
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
        return None

# --- Market Status Function ---
def is_market_open():
    now = datetime.now(ist_timezone)
    current_time = now.time()
    
    # Market Hours: 09:15 AM se 03:30 PM IST
    market_start = datetime.strptime("09:15:00", "%H:%M:%S").time()
    market_end = datetime.strptime("15:30:00", "%H:%M:%S").time()
    
    return market_start <= current_time <= market_end

# --- Test Execution ---
if __name__ == "__main__":
    print("Script execution started...")
    
    if is_market_open():
        print("Market is OPEN!")
    else:
        print("Market is CLOSED!")
    
    res = send_whatsapp("Test message: Trading Bot is Working!")
    if res is not None:
        print("Status Code:", res.status_code)
        print("Response:", res.text)