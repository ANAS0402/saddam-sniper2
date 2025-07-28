# config.py

TOKEN = '7831896600:AAG7MH7h3McjcG2ZVdkHDddzblxJABohaa0'
CHAT_ID = '1873122742'

# Binance API endpoints
BASE_URL = "https://api.binance.com"

# Settings
SNIPER_PAIRS = ["CFXUSDT", "PYTHUSDT", "JUPUSDT", "BLURUSDT", "MBOXUSDT", "PYRUSDT", "HMSTRUSDT", "AIUSDT"]
VOLUME_SPIKE_THRESHOLD = 2.5  # x times normal
WICK_RATIO_THRESHOLD = 3.0    # upper wick > lower wick * 3
DEPTH_IMBALANCE_THRESHOLD = 2.0  # bid > ask x times
