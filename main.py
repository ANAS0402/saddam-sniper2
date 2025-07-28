import requests
import time
from datetime import datetime, timedelta
from telegram import Bot
from flask import Flask
import threading

# --- CONFIG ---
TELEGRAM_TOKEN = "7831896600:AAG7MH7h3McjcG2ZVdkHDddzblxJABohaa0"
CHAT_ID = "1873122742"

COINS = ["CFX", "PNUT", "PYTH", "MBOX", "BLUR", "JUP", "ONE", "AI", "HSMTR"]
DROP_PERCENT = -6.0  # % sudden drop
DROP_TIMEFRAME = 5   # minutes
VOLUME_SPIKE_X = 2.0
WICK_THRESHOLD = 1.5  # price rebound after dump
COOLDOWN_MINUTES = 20  # cooldown per coin

# --- MEMORY TRACKER ---
last_alert_time = {}

# --- INIT ---
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# --- UTILITIES ---
def fetch_klines(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}USDT&interval=1m&limit=10"
    r = requests.get(url)
    return r.json()

def analyze_coin(symbol):
    try:
        klines = fetch_klines(symbol)
        if len(klines) < DROP_TIMEFRAME + 1:
            return

        closes = [float(k[4]) for k in klines[-DROP_TIMEFRAME-1:]]
        highs = [float(k[2]) for k in klines[-DROP_TIMEFRAME-1:]]
        lows = [float(k[3]) for k in klines[-DROP_TIMEFRAME-1:]]
        volumes = [float(k[5]) for k in klines[-DROP_TIMEFRAME-1:]]

        drop_pct = ((closes[-1] - closes[0]) / closes[0]) * 100
        avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
        wick_size = ((highs[-1] - lows[-1]) / closes[-1]) * 100

        if (
            drop_pct <= DROP_PERCENT and
            volumes[-1] > avg_volume * VOLUME_SPIKE_X and
            wick_size >= WICK_THRESHOLD and
            cooldown_ok(symbol)
        ):
            msg = (
                f"🚨 SNIPER ALERT\n\n"
                f"💣 {symbol} dropped {drop_pct:.2f}% in {DROP_TIMEFRAME}min\n"
                f"📊 Volume spike: {volumes[-1]:.2f} > avg {avg_volume:.2f}\n"
                f"📈 Wick: {wick_size:.2f}%\n"
                f"🕒 {datetime.now().strftime('%H:%M:%S')}\n\n"
                f"https://www.tradingview.com/symbols/{symbol}USDT"
            )
            bot.send_message(chat_id=CHAT_ID, text=msg)
            last_alert_time[symbol] = datetime.now()

    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")

def cooldown_ok(symbol):
    last_time = last_alert_time.get(symbol)
    if not last_time:
        return True
    return (datetime.now() - last_time) > timedelta(minutes=COOLDOWN_MINUTES)

# --- LOOP ---
def sniper_loop():
    while True:
        for coin in COINS:
            analyze_coin(coin.upper())
            time.sleep(1)
        time.sleep(30)

# --- WEB ---
@app.route('/')
def home():
    return "Saddam Sniper Running"

# --- START ---
if __name__ == '__main__':
    threading.Thread(target=sniper_loop).start()
    app.run(host="0.0.0.0", port=3000)


# Start everything
if __name__ == '__main__':
    start_bot()
    app.run(host='0.0.0.0', port=3000)
