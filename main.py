import sys
import time
import logging
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from config import TELEGRAM_BOT_TOKEN
from bot import main as start_bot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("XAUUSD_Bot_Main")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting XAUUSD Smart Money Concepts & ICT Telegram Trading Bot")
    logger.info("=" * 60)
    
    start_bot()
