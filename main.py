import sys
import time
import logging
import asyncio
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from config import PRIMARY_BOT_TOKEN, SECONDARY_BOT_TOKEN
from bot import run_bot_instance
from trademaster_bot import run_trademaster_bot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("Multi_Bot_Runner")

async def run_all_bots():
    logger.info("=" * 65)
    logger.info("Starting Multi-Bot Platform:")
    logger.info("  1. Gold Bot (@Golddddddddddddddbot) ➔ XAUUSD SMC & ICT Engine")
    logger.info("  2. TradeMaster (@Raidennnnnxbot) ➔ Indian Stock Market (NIFTY/NSE)")
    logger.info("=" * 65)

    tasks = []
    
    if PRIMARY_BOT_TOKEN:
        logger.info("🚀 Launching XAUUSD Gold Bot (@Golddddddddddddddbot)...")
        tasks.append(asyncio.create_task(run_bot_instance(PRIMARY_BOT_TOKEN)))

    if SECONDARY_BOT_TOKEN:
        logger.info("🇮🇳 Launching TradeMaster Indian Stock Bot (@Raidennnnnxbot)...")
        tasks.append(asyncio.create_task(run_trademaster_bot(SECONDARY_BOT_TOKEN)))

    if not tasks:
        logger.error("No valid Telegram Bot tokens found in .env!")
        return

    await asyncio.gather(*tasks)

def main():
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        logger.info("Service stopped by user.")
    except Exception as e:
        logger.error(f"Error in multi-bot runner: {e}")

if __name__ == "__main__":
    main()
