import threading
import time
import requests
from flask import Flask
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler

# Your credentials
BOT_TOKEN = '7831896600:AAG7MH7h3McjcG2ZVdkHDddzblxJABohaa0'
CHAT_ID = '1873122742'

# Initialize bot and Flask
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
scheduler = BackgroundScheduler()

# List of target coins
COINS = ['CFXUSDT', 'PNUTUSDT', 'PYTHUSDT', 'MBOXUSDT', 'BLURUSDT', 'JUPUSDT', 'ONEUSDT', 'AIUSDT', 'HMSTRUSDT']

# Send a message to Telegram
def notify_user(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"[📨 Telegram] {message}")
    except Exception as e:
        print(f"[⚠️ Telegram Error] {e}")

# Analyze individual coin
def analyze_coin(symbol):
    url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}'
    try:
        response = requests.get(url)
        data = response.json()
        if 'lastPrice' in data:
            price = float(data['lastPrice'])
            change = float(data['priceChangePercent'])

            # Example sniper logic
            if change >= 5:
                notify_user(f"🚀 {symbol} is pumping! Price: {price} | Change: {change:.2f}%")
            elif change <= -5:
                notify_user(f"📉 {symbol} is dumping! Price: {price} | Change: {change:.2f}%")
            else:
                print(f"[ℹ️ {symbol}] Normal activity: {change:.2f}%")
        else:
            print(f"[⚠️ INVALID DATA] {symbol}: {data}")
    except Exception as e:
        print(f"[❌ Error] Failed to analyze {symbol}: {e}")

# Loop to check all coins
def sniper_loop():
    while True:
        for coin in COINS:
            analyze_coin(coin)
        time.sleep(60)  # Wait 60 seconds between each cycle

# Flask route
@app.route('/')
def home():
    return '✅ Saddam Sniper is running.'

# Start sniper in background
def start_bot():
    threading.Thread(target=sniper_loop, daemon=True).start()
    notify_user("🟢 Saddam Sniper has started.")

# Start everything
if __name__ == '__main__':
    start_bot()
    app.run(host='0.0.0.0', port=3000)
