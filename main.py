import datetime
import time

def is_market_open():
    now = datetime.datetime.now()
    
    # Check karein ki aaj Monday se Friday (0 to 4) hai ya nahi
    if now.weekday() >= 5: # 5 = Saturday, 6 = Sunday
        return False
    
    # Market Open: 09:15 AM
    market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    # Market Close: 03:30 PM (15:30)
    market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_start <= now <= market_end

# Main Execution Loop
while True:
    if is_market_open():
        print("Market Open hai. Data fetch ho raha hai...")
        # Yahan aapka API data fetch karne ka code aayega
        
    else:
        print("Market filhal band hai. Script ko stop kiya ja raha hai...")
        break  # Loop tod kar program ko poori tarah band kar dega

    time.sleep(5)  # Har 5 seconds mein check karega
    