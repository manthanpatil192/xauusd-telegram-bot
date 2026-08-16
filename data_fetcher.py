import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from config import SYMBOL, ALT_SYMBOL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Fetches real-time and historical OHLCV data for XAUUSD across multiple timeframes.
    Supports multiple ticker fallbacks and synthetic data generation for offline/testing scenarios.
    """
    
    @staticmethod
    def fetch_ohlcv(symbol=SYMBOL, period="10d", interval="15m") -> pd.DataFrame:
        """
        Fetch OHLCV data for specified timeframe interval (e.g. '15m', '1h', '4h', '1d').
        """
        tickers_to_try = [symbol, ALT_SYMBOL, "XAUUSD=X"]
        df = pd.DataFrame()

        # yfinance uses '60m' instead of '1h'
        yf_interval = interval
        if interval == "1h":
            yf_interval = "60m"
        elif interval == "4h":
            yf_interval = "60m" # Will resample 60m to 4h

        for ticker in tickers_to_try:
            try:
                logger.info(f"Fetching XAUUSD data from ticker: {ticker} (interval: {yf_interval})")
                data = yf.download(ticker, period=period, interval=yf_interval, progress=False)
                
                if not data.empty:
                    # Clean up multi-index columns if present
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = [col[0] for col in data.columns]
                    
                    data = data.rename(columns={
                        "Open": "Open", "High": "High", "Low": "Low", 
                        "Close": "Close", "Adj Close": "Close", "Volume": "Volume"
                    })
                    
                    data = data[["Open", "High", "Low", "Close", "Volume"]].dropna()

                    # If 4h requested, resample 1h data into 4h bars
                    if interval == "4h":
                        data = DataFetcher._resample_to_4h(data)

                    if len(data) >= 20:
                        df = data
                        break
            except Exception as e:
                logger.warning(f"Failed to fetch from {ticker}: {e}")

        if df.empty:
            logger.warning("Live data fetch failed or market closed. Generating synthetic market candles for strategy analysis.")
            df = DataFetcher._generate_synthetic_gold_data(interval=interval)

        return df

    @staticmethod
    def _resample_to_4h(df_1h: pd.DataFrame) -> pd.DataFrame:
        """Resample 1H dataframe into 4H candles."""
        resampled = pd.DataFrame()
        resampled['Open'] = df_1h['Open'].resample('4h').first()
        resampled['High'] = df_1h['High'].resample('4h').max()
        resampled['Low'] = df_1h['Low'].resample('4h').min()
        resampled['Close'] = df_1h['Close'].resample('4h').last()
        resampled['Volume'] = df_1h['Volume'].resample('4h').sum()
        return resampled.dropna()

    @staticmethod
    def get_multi_timeframe_data() -> dict:
        """
        Fetch 4H (HTF), 1H (MTF), and 15M (LTF) market data for XAUUSD.
        Returns a dictionary with dataframes for each timeframe.
        """
        df_4h = DataFetcher.fetch_ohlcv(interval="4h", period="30d")
        df_1h = DataFetcher.fetch_ohlcv(interval="1h", period="14d")
        df_15m = DataFetcher.fetch_ohlcv(interval="15m", period="5d")
        
        return {
            "4h": df_4h,
            "1h": df_1h,
            "15m": df_15m
        }

    @staticmethod
    def _generate_synthetic_gold_data(interval="15m", num_bars=120) -> pd.DataFrame:
        """
        Generates realistic synthetic Gold (XAUUSD) market price data with realistic SMC setups (FVG, OB, Sweeps).
        Used when financial markets are closed on weekends or live feed is throttled.
        """
        now = datetime.now()
        freq = "15min" if interval == "15m" else ("1h" if interval in ["1h", "60m"] else "4h")
        dates = pd.date_range(end=now, periods=num_bars, freq=freq)
        
        np.random.seed(42) # Reproducible market setup for reliable verification
        base_price = 2480.0
        returns = np.random.normal(0.0001, 0.0015, num_bars)
        
        # Inject realistic SMC swing moves
        # Create a Bullish Order Block + FVG pattern around bar index 80 to 95
        price = base_price * np.exp(np.cumsum(returns))
        price[80:85] -= np.linspace(0, 12, 5) # Bearish drop forming Order Block
        price[85:90] += np.linspace(0, 25, 5) # Strong bullish displacement creating BOS + FVG
        price[95:105] -= np.linspace(0, 15, 10) # Retracement into Discount FVG/OB level
        price[105:] += np.linspace(0, 18, num_bars - 105) # Bullish continuation

        opens = price[:-1]
        closes = price[1:]
        highs = np.maximum(opens, closes) + np.abs(np.random.normal(0.5, 0.4, num_bars - 1))
        lows = np.minimum(opens, closes) - np.abs(np.random.normal(0.5, 0.4, num_bars - 1))
        volumes = np.random.randint(1000, 8000, num_bars - 1)
        
        df = pd.DataFrame({
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": volumes
        }, index=dates[1:])
        
        return df

if __name__ == "__main__":
    print("Testing DataFetcher for XAUUSD...")
    mtf_data = DataFetcher.get_multi_timeframe_data()
    for tf, df in mtf_data.items():
        print(f"\n--- Timeframe: {tf.upper()} ---")
        print(f"Candles count: {len(df)}")
        print(f"Latest Close: ${df['Close'].iloc[-1]:.2f}")
        print(df.tail(3))
