import json, os, requests, time, threading
from flask import Flask
from telegram import Bot

# --- CONFIG ---
TOKEN = "7831896600:AAG7MH7h3McjcG2ZVdkHDddzblxJABohaa0"
CHAT_ID = "1873122742"
WATCHLIST = ["CFX", "PNUT", "PYTH", "MBOX", "BLUR", "JUP", "ONE", "AI", "HSMTR"]
HISTORY_FILE = "signal_memory.json"
VOLATILITY_HISTORY = 10

app = Flask(__name__)
bot = Bot(token=TOKEN)

# --- INIT HISTORY ---
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump({}, f)

def load_memory():
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)

def update_memory(symbol, result):
    memory = load_memory()
    if symbol not in memory:
        memory[symbol] = {"results": [], "volatility": []}
    memory[symbol]["results"].append(result)
    memory[symbol]["results"] = memory[symbol]["results"][-20:]
    save_memory(memory)

def record_volatility(symbol, change):
    memory = load_memory()
    if symbol not in memory:
        memory[symbol] = {"results": [], "volatility": []}
    memory[symbol]["volatility"].append(abs(change))
    memory[symbol]["volatility"] = memory[symbol]["volatility"][-VOLATILITY_HISTORY:]
    save_memory(memory)

def get_score(symbol):
    memory = load_memory()
    if symbol not in memory or not memory[symbol]["results"]:
        return 0.0
    results = memory[symbol]["results"]
    return sum(results) / len(results)

def get_volatility(symbol):
    memory = load_memory()
    if symbol not in memory or not memory[symbol]["volatility"]:
        return 1.0
    return sum(memory[symbol]["volatility"]) / len(memory[symbol]["volatility"])

# --- SNIPER ENGINE ---
def analyze(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
        data = requests.get(url, timeout=5).json()

        price_change = float(data["priceChangePercent"])
        volume = float(data["quoteVolume"])
        last_price = float(data["lastPrice"])
        symbol_score = get_score(symbol)
        volatility = get_volatility(symbol)

        # Add learning logic
        raw_signal_strength = 0
        if abs(price_change) > 1.2:
            raw_signal_strength += 1
        if volume > 1_000_000:
            raw_signal_strength += 1
        if symbol_score > 0.3:
            raw_signal_strength += 1
        if volatility > 5:
            raw_signal_strength -= 1  # penalize wild coins

        # Only alert if score is strong enough
        if raw_signal_strength >= 2:
            msg = f"⚡️ Signal for {symbol}\n" \
                  f"Price Change: {price_change:.2f}%\n" \
                  f"Volume: ${volume:,.0f}\n" \
                  f"Score: {symbol_score:.2f}\n" \
                  f"Volatility: {volatility:.2f}\n" \
                  f"Last Price: {last_price}"
            bot.send_message(chat_id=CHAT_ID, text=msg)
            update_memory(symbol, 1)
        else:
            update_memory(symbol, 0)

        record_volatility(symbol, price_change)

    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")

def sniper_loop():
    while True:
        for coin in WATCHLIST:
            analyze(coin)
            time.sleep(1)
        time.sleep(10)

@app.route("/")
def home():
    return "SADDAM SNIPER ADAPTIVE V2 is RUNNING 🧠"

if __name__ == "__main__":
    threading.Thread(target=sniper_loop).start()
    app.run(host="0.0.0.0", port=3000)
