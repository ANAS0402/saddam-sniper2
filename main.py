# main.py

from flask import Flask
from telegram import Bot
import threading
import time
from strategy import *
from config import TOKEN, CHAT_ID, SNIPER_PAIRS

app = Flask(__name__)
bot = Bot(token=TOKEN)

def sniper_loop():
    while True:
        for symbol in SNIPER_PAIRS:
            try:
                candles = get_recent_candles(symbol)
                if candle_analysis(candles) and volume_spike(candles) and depth_imbalance(symbol):
                    message = f"🎯 SADDAM SIGNAL:\n{symbol} shows strong sniper conditions!"
                    bot.send_message(chat_id=CHAT_ID, text=message)
                    print(f"[✔️ ALERT] {symbol}")
                else:
                    print(f"[🔎 SCAN] {symbol} - No entry")
            except Exception as e:
                print(f"[⚠️ ERROR] {symbol}: {e}")
        time.sleep(60)

@app.route('/')
def home():
    return "SADDAM SNIPER ACTIVE 🧠"

if __name__ == "__main__":
    threading.Thread(target=sniper_loop).start()
    app.run(host='0.0.0.0', port=3000)
