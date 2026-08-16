import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

# Asset Config
SYMBOL = "GC=F"          # Yahoo Finance Gold Futures ticker (XAU/USD spot proxy)
ALT_SYMBOL = "XAUUSD=X"    # Alternative ticker for spot Gold vs USD
ASSET_NAME = "XAUUSD (Gold Spot / Futures)"

# Strategy & Timeframe Settings
HTF_TIMEFRAME = "4h"       # Higher Timeframe for Trend Bias (4-Hour)
MTF_TIMEFRAME = "1h"       # Medium Timeframe for Structural Zones (1-Hour)
LTF_TIMEFRAME = "15m"      # Lower Timeframe for Execution & Trigger (15-Minute)

# SMC & ICT Parameter Tuning
FVG_THRESHOLD_PERCENT = 0.05    # Minimum % gap size to consider a valid Fair Value Gap
OB_SWING_LOOKBACK = 15          # Swing high/low lookback bars for Order Block detection
LIQUIDITY_LOOKBACK = 20         # Bars to scan for Equal Highs / Lows (EQH/EQL)
PREMIUM_DISCOUNT_EQUILIBRIUM = 0.50  # 50% Fibonacci Equilibrium level

# Risk Management
DEFAULT_SL_PIPS = 3.0          # Fallback SL buffer in Gold dollars ($3.00)
MIN_RISK_REWARD = 2.0          # Minimum 1:2 R:R required for valid signal
TP1_RR = 2.0                   # TP1 at 1:2 Risk to Reward
TP2_RR = 3.5                   # TP2 at 1:3.5 Risk to Reward

# News Filter Settings
NEWS_BLACKOUT_MINUTES_BEFORE = 30  # Stop trading 30 mins before high impact news
NEWS_BLACKOUT_MINUTES_AFTER = 30   # Resume trading 30 mins after high impact news
