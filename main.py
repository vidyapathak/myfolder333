import time
from datetime import datetime, timedelta, timezone

# 1. India Timezone (IST = UTC + 5:30) set karein
ist_timezone = timezone(timedelta(hours=5, minutes=30))
import time
from datetime import datetime, timedelta, timezone

# 1. India Timezone (IST = UTC + 5:30) set karein
ist_timezone = timezone(timedelta(hours=5, minutes=30))

# --- Yahan WhatsApp Function aa gaya ---
import requests


def send_whatsapp(message):
  account_sid = 'AC3a2a1efbd6aa8126995ca1db72034019'
  auth_token = 'a9dd4076ad7a4da56d78aa3d64065d1d'

  url = f'https://api.twilio.org/2010-04-01/Accounts/{account_sid}/Messages.json'

  payload = {
      'From': 'whatsapp:+17372508034',
      'To': 'whatsapp:+919303520446',
      'Body': message,
  }

  try:
    requests.post(url, data=payload, auth=(account_sid, auth_token))
  except Exception as e:
    print(f'WhatsApp Error: {e}')


# --- Aapka Purana Code Yahan Se Start Hoga ---
def is_market_open():
  now = datetime.now(ist_timezone)
  ...
def is_market_open():
    now = datetime.now(ist_timezone)
    current_time = now.time()
    
    # Market Hours: 09:15 AM se 03:30 PM IST
    market_start = datetime.strptime("09:15:00", "%H:%M:%S").time()
    market_end = datetime.strptime("15:30:00", "%H:%M:%S").time()
    
    # Check karein ki current time market hours ke andar hai ya nahi
    return market_start <= current_time <= market_end

def main():
    now_ist = datetime.now(ist_timezone)
    print(f"Current India Time (IST): {now_ist.strftime('%I:%M:%S %p')}")
    
    if not is_market_open():
        print("Market filhal band hai. Script ko stop kiya ja raha hai...")
        return

    print("Market Open hai! Live trading start ho rahi hai...")
    
    # Aapka main trading loop yahan chalega
    while is_market_open():
        current = datetime.now(ist_timezone)
        print(f"[{current.strftime('%I:%M:%S %p')}] Market Live hai, stocks scan ho rahe hain...")
        
        # Yahan aapka baaki ka trading/strategy code chalega
        
        time.sleep(60)  # Har 1 minute par repeat karega

    print("Market shaam 3:30 PM par close ho gaya. Bot stop ho gaya.")

if __name__ == "__main__":
    send_whatsapp("🚀 Testing WhatsApp Alert from VS Code!")
    main()