import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

# Asset Config
SYMBOL = "GC=F"
ALT_SYMBOL = "XAUUSD=X"
ASSET_NAME = "XAUUSD (Gold Spot / Futures)"

# Strategy & Timeframe Settings
HTF_TIMEFRAME = "4h"
MTF_TIMEFRAME = "1h"
LTF_TIMEFRAME = "15m"

# SMC & ICT Parameter Tuning
FVG_THRESHOLD_PERCENT = 0.05
OB_SWING_LOOKBACK = 15
LIQUIDITY_LOOKBACK = 20
PREMIUM_DISCOUNT_EQUILIBRIUM = 0.50

# Risk Management
DEFAULT_SL_PIPS = 3.0
MIN_RISK_REWARD = 2.0
TP1_RR = 2.0
TP2_RR = 3.5

# News Filter Settings
NEWS_BLACKOUT_MINUTES_BEFORE = 30
NEWS_BLACKOUT_MINUTES_AFTER = 30

# 🌱 Eco-Friendly Bot & Energy Optimization Settings
ECO_MODE_DEFAULT = True           # Enable Eco-Mode by default to minimize compute & energy consumption
CPU_ENERGY_SAVED_PER_SCAN_GRAMS_CO2 = 0.15  # CO2 grams saved per optimized compute scan
TREE_OFFSET_RATIO = 20.0          # 20 profitable trades = 1 tree planted offset milestone
CACHE_CHARTS_IN_ECO_MODE = True    # Caches chart PNG rendering to conserve GPU/CPU power
