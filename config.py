import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Primary & Secondary Telegram Bot Tokens
PRIMARY_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8781505939:AAGYRvN97ddYDxLIXu4sdl_MV_HC-CCAQgw")
SECONDARY_BOT_TOKEN = os.getenv("SECONDARY_BOT_TOKEN", "")

# List of all active Bot Tokens
TELEGRAM_BOT_TOKENS = [t.strip() for t in [PRIMARY_BOT_TOKEN, SECONDARY_BOT_TOKEN] if t.strip()]

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

# 🌱 Eco-Friendly Bot Settings
ECO_MODE_DEFAULT = True
CPU_ENERGY_SAVED_PER_SCAN_GRAMS_CO2 = 0.15
TREE_OFFSET_RATIO = 20.0
CACHE_CHARTS_IN_ECO_MODE = True
