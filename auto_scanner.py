import time
import logging
from pathlib import Path
from datetime import datetime

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from signal_generator import SignalGenerator
from data_fetcher import DataFetcher
from chart_generator import ChartGenerator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("AutoScanner")

def run_automated_scanner(interval_minutes=15):
    """
    Continuous background market scanner for XAUUSD.
    Scans every 15 minutes for new SMC/ICT trade setups and generates signals automatically.
    """
    logger.info("🚀 XAUUSD Automated Background Market Scanner Started...")
    logger.info(f"Scanning interval: Every {interval_minutes} minutes.")

    while True:
        try:
            logger.info("🔍 Scanning XAUUSD 4H, 1H, 15M market structure for SMC setups...")
            
            # Generate signal
            signal = SignalGenerator.generate_signal()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"[{timestamp}] Signal Evaluated: {signal['action']} ({signal['confidence_stars']})")
            logger.info(f"Entry: ${signal['entry']:.2f} | SL: ${signal['sl']:.2f} | TP1: ${signal['tp1']:.2f} | TP2: ${signal['tp2']:.2f}")

            # Generate dark-mode annotated chart PNG
            df_1h = DataFetcher.fetch_ohlcv(interval="1h")
            chart_path = ChartGenerator.generate_signal_chart(df_1h, signal, "latest_signal_chart.png")
            logger.info(f"Updated chart PNG saved to: {chart_path}")

            # Send to Telegram Channel if Bot Token and Channel ID are configured
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID:
                try:
                    import requests
                    bot_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
                    msg_text = SignalGenerator.format_telegram_signal(signal)
                    
                    with open(chart_path, "rb") as photo:
                        payload = {
                            "chat_id": TELEGRAM_CHANNEL_ID,
                            "caption": msg_text,
                            "parse_mode": "HTML"
                        }
                        files = {"photo": photo}
                        res = requests.post(bot_url, data=payload, files=files, timeout=10)
                        if res.status_code == 200:
                            logger.info("✅ Signal & Chart successfully broadcasted to Telegram Channel!")
                        else:
                            logger.warning(f"Telegram API response: {res.text}")
                except Exception as e:
                    logger.error(f"Failed to post signal to Telegram: {e}")

        except Exception as e:
            logger.error(f"Error during scan cycle: {e}")

        logger.info(f"Sleeping for {interval_minutes} minutes until next market scan...\n")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    run_automated_scanner(interval_minutes=15)
