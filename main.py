import yfinance as yf

def get_market_summary():
    # Aap jin bhi stocks ya indices ka data dekhna chahte hain yahan add kar sakte hain
    tickers = {
        'NIFTY 50': '^NSEI',
        'BANK NIFTY': '^NSEBANK',
        'RELIANCE': 'RELIANCE.NS',
        'TCS': 'TCS.NS',
        'INFY': 'INFY.NS'
    }
    
    print("\n==========================================")
    print("📊 TODAY'S MARKET SUMMARY")
    print("==========================================\n")
    
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="2d")
            
            if len(df) >= 2:
                prev_close = df['Close'].iloc[-2]
                curr_close = df['Close'].iloc[-1]
                high = df['High'].iloc[-1]
                low = df['Low'].iloc[-1]
                open_price = df['Open'].iloc[-1]
                
                change = curr_close - prev_close
                percent_change = (change / prev_close) * 100
                
                status = "🟢 GREEN" if change >= 0 else "🔴 RED"
                
                print(f"[{status}] {name}")
                print(f"  • Close : {curr_close:.2f} ({change:+.2f}, {percent_change:+.2f}%)")
                print(f"  • Open  : {open_price:.2f}")
                print(f"  • High  : {high:.2f}")
                print(f"  • Low   : {low:.2f}")
                print("-" * 42)
        except Exception as e:
            print(f"Error fetching data for {name}: {e}")

if __name__ == "__main__":
    get_market_summary()