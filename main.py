import sys
import time
import logging
import asyncio
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from config import TELEGRAM_BOT_TOKENS, PRIMARY_BOT_TOKEN, SECONDARY_BOT_TOKEN
from bot import run_bot_instance

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("XAUUSD_Multi_Bot_Main")

async def run_all_bots():
    logger.info("=" * 60)
    logger.info("Starting Multi-Bot High-Precision XAUUSD Signal Service")
    logger.info(f"Active Bot Tokens Configured: {len(TELEGRAM_BOT_TOKENS)}")
    logger.info("=" * 60)

    if not TELEGRAM_BOT_TOKENS:
        logger.error("No Telegram Bot tokens configured in .env!")
        return

    # Create concurrent background tasks for each bot token
    tasks = []
    for idx, token in enumerate(TELEGRAM_BOT_TOKENS, 1):
        logger.info(f"🚀 Launching Bot Instance #{idx}...")
        tasks.append(asyncio.create_task(run_bot_instance(token)))

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
