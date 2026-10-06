import os
import time
from dotenv import load_dotenv
from SmartApi import SmartConnect
import pyotp
import pandas as pd
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# --- LIVE TRADING & DYNAMIC LOT SETTINGS ---
MAX_PROB_LOT_SIZE = 4   
BASE_LOT_SIZE = 1        
LOT_QUANTITY = 15        
TRADING_SYMBOL = "NIFTY"
EXCHANGE_SEGMENT = "NSE"
PRODUCT_TYPE = "INTRADAY"

def connect_angel_one():
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            obj = SmartConnect(api_key=API_KEY)
            totp = pyotp.TOTP(TOTP_SECRET).now()
            data = obj.generateSession(CLIENT_ID, MPIN, totp)
            
            if data and data.get('status'):
                print("🚀 Login Successful! Live Session Active.")
                return obj
            else:
                print(f"❌ Login Failed (Attempt {attempt}): {data.get('message', 'Unknown Error')}")
        except Exception as e:
            print(f"⚠️️ Connection Error (Attempt {attempt}): {e}")
        
        if attempt < max_retries:
            print("⏳ 5 seconds mein dobara koshish kar rahe hain...")
            time.sleep(5)
            
    return None

def is_market_open_day():
    """Check karta hai ki aaj Monday se Friday ke beech ka din hai ya nahi (0 = Monday, 4 = Friday)"""
    current_day = datetime.now().weekday()
    if current_day >= 5:  # 5 matlab Saturday, 6 matlab Sunday
        return False
    return True

def calculate_indicators(df, period=14):
    df['High'] = pd.to_numeric(df['High'])
    df['Low'] = pd.to_numeric(df['Low'])
    df['Close'] = pd.to_numeric(df['Close'])
    
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    return df

def determine_dynamic_lots_with_fallback(session, setup_type, entry_price):
    desired_lots = MAX_PROB_LOT_SIZE if setup_type == "HIGH_PROBABILITY" else BASE_LOT_SIZE
    available_cash = 999999.0
    
    try:
        fund_data = session.getRMS()
        if fund_data and 'data' in fund_data:
            available_cash = float(fund_data['data'].get('net', 0))
    except Exception:
        try:
            fund_data = session.getMargin()
            if fund_data and 'data' in fund_data:
                available_cash = float(fund_data['data'].get('availablecash', 0))
        except Exception:
            pass

    margin_per_lot = (entry_price * LOT_QUANTITY) / 5 
    possible_lots = desired_lots
    
    while possible_lots >= 1:
        required_margin = margin_per_lot * possible_lots
        if available_cash >= required_margin:
            break
        possible_lots -= 1  
        
    if possible_lots == 0:
        return 0, "Insufficient_Funds"
    return possible_lots, f"Approved_{possible_lots}_Lots"

def place_live_order(session, token, symbol, transaction_type, quantity, price):
    try:
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": transaction_type,
            "exchange": EXCHANGE_SEGMENT,
            "ordertype": "MARKET",
            "producttype": PRODUCT_TYPE,
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(quantity)
        }
        
        order_id = session.placeOrder(order_params)
        print(f"🔥 LIVE ORDER PLACED! Order ID: {order_id}")
        return order_id, "SUCCESS"
    except Exception as e:
        print(f"❌ Order Placement Error: {e}")
        return None, str(e)

def log_live_trade(timestamp, signal, entry, sl, tgt, lots, order_status):
    log_file = "live_executed_trades.csv"
    new_data = pd.DataFrame([[timestamp, TRADING_SYMBOL, signal, entry, sl, tgt, lots, order_status]], 
                            columns=["Timestamp", "Symbol", "Signal", "Entry Price", "Stop Loss", "Target", "Lots", "Status"])
    
    if not os.path.exists(log_file):
        new_data.to_csv(log_file, index=False)
    else:
        new_data.to_csv(log_file, mode='a', header=False, index=False)

if __name__ == "__main__":
    # --- WEEKEND FILTER CHECK ---
    if not is_market_open_day():
        print("🛑 Aaj Weekend (Saturday/Sunday) hai! Stock market band hai, isliye bot run nahi hoga.")
        exit()
        
    session = connect_angel_one()
    
    if session:
        print("📊 Live Session Active! Bot weekday trading ke liye taiyar hai...")
        try:
            token = "99926000"
            params = {
                "symboltoken": token,
                "exchange": EXCHANGE_SEGMENT,
                "interval": "ONE_MINUTE",
                "fromdate": datetime.now().strftime('%Y-%m-%d 09:15'),
                "todate": datetime.now().strftime('%Y-%m-%d %H:%M')
            }
            
            historical_data = session.getCandleData(params)
            
            if historical_data and 'data' in historical_data:
                df = pd.DataFrame(historical_data['data'], columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df = calculate_indicators(df)
                
                target_index = len(df) - 2 
                if target_index < 0:
                    print("⏳ Market data abhi poori tarah update nahi hua hai.")
                    exit()
                    
                candle_time = df['Time'].iloc[target_index]
                last_close = df['Close'].iloc[target_index]
                last_sma = df['SMA_20'].iloc[target_index]
                last_atr = df['ATR'].iloc[target_index]
                avg_atr = df['ATR'].mean()
                
                print(f"📉 Time: {candle_time} | Close: {last_close} | SMA 20: {last_sma:.2f} | ATR: {last_atr:.2f}")
                
                if last_atr > (avg_atr * 1.8):
                    print("⚠️️ HIGH VOLATILITY: Market bohot volatile hai, live trade nahi liya jayega!")
                    exit()

                trend_strength = abs(last_close - last_sma)
                setup_type = "HIGH_PROBABILITY" if trend_strength > (last_atr * 1.5) else "NORMAL_STRONG"

                prev_close = df['Close'].iloc[target_index - 1]
                prev_sma = df['SMA_20'].iloc[target_index - 1]
                
                if last_close > last_sma and prev_close > prev_sma:
                    current_signal = "BUY"
                elif last_close < last_sma and prev_close < prev_sma:
                    current_signal = "SELL"
                else:
                    print("⏳ Clear trend nahi hai, intezar kar rahe hain...")
                    exit()
                
                atr_multiplier = 1.5
                target_multiplier = 3.0
                if current_signal == "BUY":
                    stop_loss = round(last_close - (last_atr * atr_multiplier), 2)
                    target = round(last_close + (last_atr * target_multiplier), 2)
                else:
                    stop_loss = round(last_close + (last_atr * atr_multiplier), 2)
                    target = round(last_close - (last_atr * target_multiplier), 2)
                
                allocated_lots, trade_status = determine_dynamic_lots_with_fallback(session, setup_type, last_close)
                
                if allocated_lots > 0:
                    total_qty = allocated_lots * LOT_QUANTITY
                    print(f"🚀 Signal Confirmed [{current_signal}] | Setup: {setup_type} | Executing {total_qty} Quantity ({allocated_lots} Lots)...")
                    
                    order_id, execution_status = place_live_order(session, token, TRADING_SYMBOL, current_signal, total_qty, last_close)
                    log_live_trade(str(candle_time), current_signal, last_close, stop_loss, target, allocated_lots, execution_status)
                    print("📁 Live trade record 'live_executed_trades.csv' mein save ho gaya hai!")
                else:
                    print(f"❌ Trade Blocked due to funds: {trade_status}")
                
            else:
                print("⚠️ Data format ya API response mein kuch gadbadi hai.")
                
        except Exception as e:
            print(f"❌ Live Strategy Execution Error: {e}")
    else:
        print("❌ Sabhi login attempts fail ho gaye.")