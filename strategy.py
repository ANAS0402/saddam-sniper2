# strategy.py

import requests
from config import BASE_URL, VOLUME_SPIKE_THRESHOLD, WICK_RATIO_THRESHOLD, DEPTH_IMBALANCE_THRESHOLD

def get_recent_candles(symbol):
    url = f"{BASE_URL}/api/v3/klines?symbol={symbol}&interval=1m&limit=10"
    data = requests.get(url).json()
    return data

def candle_analysis(candles):
    last = candles[-1]
    open_, high, low, close, volume = float(last[1]), float(last[2]), float(last[3]), float(last[4]), float(last[5])
    upper_wick = high - max(open_, close)
    lower_wick = min(open_, close) - low
    if lower_wick == 0:
        return False
    wick_ratio = upper_wick / lower_wick
    return wick_ratio > WICK_RATIO_THRESHOLD

def volume_spike(candles):
    volumes = [float(c[5]) for c in candles[:-1]]
    avg_vol = sum(volumes) / len(volumes)
    latest_vol = float(candles[-1][5])
    return latest_vol > avg_vol * VOLUME_SPIKE_THRESHOLD

def depth_imbalance(symbol):
    url = f"{BASE_URL}/api/v3/depth?symbol={symbol}&limit=10"
    data = requests.get(url).json()
    bid_qty = sum([float(q[1]) for q in data['bids']])
    ask_qty = sum([float(q[1]) for q in data['asks']])
    if ask_qty == 0:
        return False
    imbalance = bid_qty / ask_qty
    return imbalance > DEPTH_IMBALANCE_THRESHOLD
