import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from config import FVG_THRESHOLD_PERCENT, OB_SWING_LOOKBACK, PREMIUM_DISCOUNT_EQUILIBRIUM

class SMCAnalyzer:
    """
    Core Smart Money Concepts (SMC) & Inner Circle Trader (ICT) Analysis Engine.
    Detects:
      - Swing Highs & Swing Lows
      - Break of Structure (BOS) & Change of Character (CHOCH)
      - Fair Value Gaps (FVG)
      - Bullish & Bearish Order Blocks (OB)
      - Liquidity Sweeps (EQH / EQL Liquidity Grab)
      - Premium vs Discount 50% Equilibrium Zones
      - Key Support & Resistance (S/R) levels
    """

    @staticmethod
    def analyze_market(df: pd.DataFrame, timeframe: str = "1h") -> dict:
        """
        Runs comprehensive SMC, ICT & S/R analysis on the provided DataFrame.
        """
        if df.empty or len(df) < 30:
            return {"error": "Insufficient market data for SMC analysis"}

        df = df.copy()

        # 1. Swing Highs & Lows
        swings = SMCAnalyzer._find_swings(df, window=5)
        
        # 2. Market Structure (BOS / CHOCH)
        structure = SMCAnalyzer._detect_market_structure(df, swings)
        
        # 3. Fair Value Gaps (FVG)
        fvgs = SMCAnalyzer._detect_fvgs(df)
        
        # 4. Order Blocks (OB)
        order_blocks = SMCAnalyzer._detect_order_blocks(df, swings)

        # 5. Liquidity Sweeps (EQH / EQL)
        liquidity = SMCAnalyzer._detect_liquidity_sweeps(df, swings)

        # 6. Premium vs Discount Zone
        eq_data = SMCAnalyzer._calculate_premium_discount(df, swings)

        # 7. Support & Resistance Pivot Levels
        sr_levels = SMCAnalyzer._calculate_sr_levels(df)

        return {
            "timeframe": timeframe,
            "current_price": float(df["Close"].iloc[-1]),
            "structure": structure,
            "swings": swings,
            "fvgs": fvgs,
            "order_blocks": order_blocks,
            "liquidity": liquidity,
            "premium_discount": eq_data,
            "sr_levels": sr_levels
        }

    @staticmethod
    def _find_swings(df: pd.DataFrame, window: int = 5) -> dict:
        """Identifies Swing Highs and Swing Lows."""
        highs = df["High"].values
        lows = df["Low"].values
        
        swing_highs = []
        swing_lows = []

        for i in range(window, len(df) - window):
            # Swing High: Highest high in surrounding window
            if highs[i] == max(highs[i - window : i + window + 1]):
                swing_highs.append({
                    "index": i,
                    "timestamp": df.index[i],
                    "price": float(highs[i])
                })
            # Swing Low: Lowest low in surrounding window
            if lows[i] == min(lows[i - window : i + window + 1]):
                swing_lows.append({
                    "index": i,
                    "timestamp": df.index[i],
                    "price": float(lows[i])
                })

        last_swing_high = swing_highs[-1] if swing_highs else {"price": float(df["High"].max())}
        last_swing_low = swing_lows[-1] if swing_lows else {"price": float(df["Low"].min())}

        return {
            "all_highs": swing_highs,
            "all_lows": swing_lows,
            "last_high": last_swing_high,
            "last_low": last_swing_low
        }

    @staticmethod
    def _detect_market_structure(df: pd.DataFrame, swings: dict) -> dict:
        """Detects Trend Direction, BOS (Break of Structure) & CHOCH (Change of Character)."""
        current_close = df["Close"].iloc[-1]
        last_high = swings["last_high"]["price"]
        last_low = swings["last_low"]["price"]

        # Default trend determination based on recent swing sequence
        highs = [sh["price"] for sh in swings["all_highs"][-3:]]
        lows = [sl["price"] for sl in swings["all_lows"][-3:]]

        trend = "BULLISH"
        bos_status = "NEUTRAL"
        choch_status = "NEUTRAL"

        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                trend = "BULLISH"
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                trend = "BEARISH"
            else:
                trend = "RANGING / SIDEWAYS"

        # Check for recent Break of Structure or CHOCH on latest candles
        recent_close = df["Close"].iloc[-5:]
        
        if (recent_close > last_high).any():
            if trend == "BULLISH":
                bos_status = "BULLISH_BOS" # Continuation break above swing high
            else:
                choch_status = "BULLISH_CHOCH" # Trend reversal break above swing high

        if (recent_close < last_low).any():
            if trend == "BEARISH":
                bos_status = "BEARISH_BOS" # Continuation break below swing low
            else:
                choch_status = "BEARISH_CHOCH" # Trend reversal break below swing low

        return {
            "trend": trend,
            "bos": bos_status,
            "choch": choch_status,
            "last_high": last_high,
            "last_low": last_low
        }

    @staticmethod
    def _detect_fvgs(df: pd.DataFrame) -> dict:
        """Detects Bullish & Bearish Fair Value Gaps (FVG) / Imbalances."""
        bullish_fvgs = []
        bearish_fvgs = []
        
        highs = df["High"].values
        lows = df["Low"].values
        closes = df["Close"].values
        timestamps = df.index

        current_price = closes[-1]

        # Scan recent candles for 3-candle FVG patterns
        for i in range(2, len(df)):
            # Bullish FVG: Low of candle i > High of candle i-2
            if lows[i] > highs[i - 2]:
                gap_bottom = highs[i - 2]
                gap_top = lows[i]
                gap_size = gap_top - gap_bottom
                
                # Filter for valid gap size and fresh/unmitigated FVGs (price hasn't completely filled gap)
                if gap_size / current_price * 100 >= FVG_THRESHOLD_PERCENT:
                    is_mitigated = (df["Low"].iloc[i+1:] < gap_bottom).any() if i < len(df) - 1 else False
                    bullish_fvgs.append({
                        "top": float(gap_top),
                        "bottom": float(gap_bottom),
                        "midpoint": float((gap_top + gap_bottom) / 2),
                        "size": float(gap_size),
                        "timestamp": timestamps[i],
                        "mitigated": is_mitigated
                    })

            # Bearish FVG: High of candle i < Low of candle i-2
            if highs[i] < lows[i - 2]:
                gap_top = lows[i - 2]
                gap_bottom = highs[i]
                gap_size = gap_top - gap_bottom

                if gap_size / current_price * 100 >= FVG_THRESHOLD_PERCENT:
                    is_mitigated = (df["High"].iloc[i+1:] > gap_top).any() if i < len(df) - 1 else False
                    bearish_fvgs.append({
                        "top": float(gap_top),
                        "bottom": float(gap_bottom),
                        "midpoint": float((gap_top + gap_bottom) / 2),
                        "size": float(gap_size),
                        "timestamp": timestamps[i],
                        "mitigated": is_mitigated
                    })

        # Filter active (unmitigated) gaps nearest to current price
        active_bullish = [f for f in bullish_fvgs if not f["mitigated"] and f["top"] <= current_price * 1.01]
        active_bearish = [f for f in bearish_fvgs if not f["mitigated"] and f["bottom"] >= current_price * 0.99]

        return {
            "all_bullish": bullish_fvgs,
            "all_bearish": bearish_fvgs,
            "active_bullish": active_bullish[-2:] if active_bullish else [],
            "active_bearish": active_bearish[-2:] if active_bearish else []
        }

    @staticmethod
    def _detect_order_blocks(df: pd.DataFrame, swings: dict) -> dict:
        """Detects Bullish & Bearish Institutional Order Blocks (OB)."""
        bullish_obs = []
        bearish_obs = []

        opens = df["Open"].values
        closes = df["Close"].values
        highs = df["High"].values
        lows = df["Low"].values
        timestamps = df.index

        # Scan for high-volume candles prior to strong displacement
        for i in range(5, len(df) - 2):
            # Bullish Order Block: Red/bearish candle prior to strong upward displacement
            if closes[i] < opens[i]:  # Red candle
                future_move = closes[i + 2] - closes[i]
                if future_move > 5.0: # Strong Gold expansion ($5+ move)
                    bullish_obs.append({
                        "top": float(highs[i]),
                        "bottom": float(lows[i]),
                        "midpoint": float((highs[i] + lows[i]) / 2),
                        "timestamp": timestamps[i],
                        "type": "Bullish OB"
                    })

            # Bearish Order Block: Green/bullish candle prior to strong downward displacement
            if closes[i] > opens[i]:  # Green candle
                future_move = closes[i] - closes[i + 2]
                if future_move > 5.0: # Strong Gold decline ($5+ drop)
                    bearish_obs.append({
                        "top": float(highs[i]),
                        "bottom": float(lows[i]),
                        "midpoint": float((highs[i] + lows[i]) / 2),
                        "timestamp": timestamps[i],
                        "type": "Bearish OB"
                    })

        last_bullish_ob = bullish_obs[-1] if bullish_obs else None
        last_bearish_ob = bearish_obs[-1] if bearish_obs else None

        return {
            "bullish_ob": last_bullish_ob,
            "bearish_ob": last_bearish_ob,
            "all_bullish": bullish_obs[-3:],
            "all_bearish": bearish_obs[-3:]
        }

    @staticmethod
    def _detect_liquidity_sweeps(df: pd.DataFrame, swings: dict) -> dict:
        """Detects Liquidity Raids / Sweeps over Equal Highs (EQH) or Equal Lows (EQL)."""
        recent_candles = df.tail(10)
        current_price = df["Close"].iloc[-1]
        
        last_high = swings["last_high"]["price"]
        last_low = swings["last_low"]["price"]

        sweep_high = False
        sweep_low = False

        # Liquidity Sweep High: High wicks above swing high but Close finishes below it
        for _, row in recent_candles.iterrows():
            if row["High"] > last_high and row["Close"] < last_high:
                sweep_high = True

            if row["Low"] < last_low and row["Close"] > last_low:
                sweep_low = True

        return {
            "sweep_high": sweep_high,
            "sweep_low": sweep_low,
            "eqh_level": last_high,
            "eql_level": last_low
        }

    @staticmethod
    def _calculate_premium_discount(df: pd.DataFrame, swings: dict) -> dict:
        """Calculates ICT Premium vs Discount Equilibrium (50% level of swing range)."""
        last_high = swings["last_high"]["price"]
        last_low = swings["last_low"]["price"]
        current_price = df["Close"].iloc[-1]

        swing_range = max(last_high - last_low, 1.0)
        equilibrium = last_low + (swing_range * PREMIUM_DISCOUNT_EQUILIBRIUM)
        
        pct_position = (current_price - last_low) / swing_range * 100

        zone = "DISCOUNT" if current_price < equilibrium else "PREMIUM"

        return {
            "swing_high": last_high,
            "swing_low": last_low,
            "equilibrium_50pct": float(equilibrium),
            "current_price": float(current_price),
            "zone": zone,
            "position_percent": float(pct_position)
        }

    @staticmethod
    def _calculate_sr_levels(df: pd.DataFrame) -> dict:
        """Calculates Pivot Support & Resistance key price zones."""
        recent = df.tail(50)
        pdh = float(recent["High"].max()) # Previous Day/Period High
        pdl = float(recent["Low"].min())  # Previous Day/Period Low
        pivot = float((pdh + pdl + recent["Close"].iloc[-1]) / 3)

        r1 = float((2 * pivot) - pdl)
        s1 = float((2 * pivot) - pdh)
        r2 = float(pivot + (pdh - pdl))
        s2 = float(pivot - (pdh - pdl))

        return {
            "pdh": pdh,
            "pdl": pdl,
            "pivot": pivot,
            "r1": r1,
            "s1": s1,
            "r2": r2,
            "s2": s2
        }

if __name__ == "__main__":
    from data_fetcher import DataFetcher
    print("Testing SMCAnalyzer module...")
    df_1h = DataFetcher.fetch_ohlcv(interval="1h")
    analysis = SMCAnalyzer.analyze_market(df_1h, timeframe="1h")
    print(f"Current Gold Price: ${analysis['current_price']:.2f}")
    print(f"Structure Trend: {analysis['structure']['trend']}")
    print(f"Premium/Discount Zone: {analysis['premium_discount']['zone']}")
    print(f"Active Bullish FVGs: {len(analysis['fvgs']['active_bullish'])}")
    print(f"Bullish OB: {analysis['order_blocks']['bullish_ob']}")
