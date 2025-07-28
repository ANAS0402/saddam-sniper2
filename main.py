import requests, time, threading
from telegram import Bot
from flask import Flask
import logging
import numpy as np

TOKEN = "7831896600:AAG7MH7h3McjcG2ZVdkHDddzblxJABohaa0"
CHAT_ID = "1873122742"

bot = Bot(token=TOKEN)
app = Flask(__name__)

COINS = ["CFXUSDT", "PYTHUSDT", "PYRUSDT", "MBOXUSDT", "HMSTRUSDT", "JUPUSDT", "BLURUSDT", "AIUSDT", "ONEUSDT", "PNUTUSDT"]
BASE_URL = "https://api.binance.com/api/v3/"

alerted = {}  # coin: last alert timestamp

def get_klines(symbol, interval="1m", limit=100):
    url = BASE_URL + "klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [float(i[4]) for i in data]  # closing prices
    except:
        return None

def market_regime(prices):
    if not prices: return False
    returns = np.diff(prices) / prices[:-1]
    volatility = np.std(returns)
    trend_strength = abs(prices[-1] - prices[0]) / prices[0]
    return trend_strength > 0.01 and volatility > 0.003  # trend and action

def volume_breakout(symbol):
    url = BASE_URL + "ticker/24hr"
    try:
        r = requests.get(url, params={"symbol": symbol}, timeout=5)
        data = r.json()
        vol_now = float(data["quoteVolume"])
        price_now = float(data["lastPrice"])
        change = float(data["priceChangePercent"])
        return vol_now > 1_000_000 and abs(change) > 2.5
    except:
        return False

def calculate_conviction(prices):
    if not prices: return 0
    recent = prices[-10:]
    trend = (recent[-1] - recent[0]) / recent[0]
    returns = np.diff(recent) / recent[:-1]
    vol = np.std(returns)
    zscore = (recent[-1] - np.mean(recent)) / (np.std(recent) + 1e-9)
    return (abs(trend) * 50 + vol * 100 + abs(zscore) * 30)  # out of ~180

def should_alert(symbol):
    now = time.time()
    if symbol in alerted and now - alerted[symbol] < 300:
        return False
    prices = get_klines(symbol)
    if not market_regime(prices): return False
    if not volume_breakout(symbol): return False
    score = calculate_conviction(prices)
    if score < 80: return False
    alerted[symbol] = now
    return True

def send_alert(symbol):
    r = requests.get(BASE_URL + "ticker/price", params={"symbol": symbol})
    data = r.json()
    price = float(data["price"])
    msg = f"🔥 Entry Alert: {symbol}\nPrice: {price:.4f}\nConviction: HIGH\nTime: {time.strftime('%H:%M:%S')}"
    bot.send_message(chat_id=CHAT_ID, text=msg)

def sniper_loop():
    while True:
        for coin in COINS:
            try:
                if should_alert(coin):
                    send_alert(coin)
            except Exception as e:
                print(f"Error analyzing {coin}: {e}")
        time.sleep(30)

@app.route('/')
def home():
    return "🟢 SADDAM SNIPER RUNNING"

if __name__ == "__main__":
    logging.getLogger('werkzeug').disabled = True
    threading.Thread(target=sniper_loop).start()
    app.run(host='0.0.0.0', port=3000)
