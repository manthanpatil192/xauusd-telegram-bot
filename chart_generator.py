import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from pathlib import Path
from data_fetcher import DataFetcher

class ChartGenerator:
    """
    Generates annotated dark-mode candlestick chart images for XAUUSD & Indian Stock Breakouts
    showing Entry, Stop Loss, Target lines, Resistance Breakout lines, and Volume Expansion subplots.
    """

    @staticmethod
    def generate_signal_chart(df: pd.DataFrame, signal_data: dict, output_path: str = "chart.png") -> str:
        if df.empty:
            df = DataFetcher.fetch_ohlcv(interval="1h")

        df = df.tail(40).copy()

        plt.style.use("dark_background")
        
        # Create figure with 2 subplots: Price Chart (75% height) + Volume Subplot (25% height)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), dpi=150, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        fig.patch.set_facecolor("#12141D")
        ax1.set_facecolor("#181B26")
        ax2.set_facecolor("#181B26")

        indexes = np.arange(len(df))
        opens = df["Open"].values
        highs = df["High"].values
        lows = df["Low"].values
        closes = df["Close"].values
        volumes = df["Volume"].values if "Volume" in df else np.zeros(len(df))

        for i in range(len(df)):
            color = "#00E676" if closes[i] >= opens[i] else "#FF5252"
            ax1.plot([indexes[i], indexes[i]], [lows[i], highs[i]], color=color, linewidth=1.2)
            body_bottom = min(opens[i], closes[i])
            body_top = max(opens[i], closes[i])
            body_height = max(body_top - body_bottom, 0.10)
            rect = plt.Rectangle((indexes[i] - 0.35, body_bottom), 0.7, body_height, facecolor=color, edgecolor=color, alpha=0.9)
            ax1.add_patch(rect)

            # Volume bars in subplot 2
            vol_color = "#00E676" if closes[i] >= opens[i] else "#FF5252"
            ax2.bar(indexes[i], volumes[i], color=vol_color, alpha=0.75, width=0.7)

        # Highlight breakout candle volume spike on last bar
        if len(volumes) > 0:
            ax2.bar(indexes[-1], volumes[-1], color="#76FF03", alpha=1.0, width=0.8, edgecolor="#FFFFFF", label="Breakout Volume Spike")

        entry = signal_data.get("entry", closes[-1])
        sl = signal_data.get("sl", entry * 0.97)
        tp1 = signal_data.get("tp1") or signal_data.get("target1", entry * 1.05)
        tp2 = signal_data.get("tp2") or signal_data.get("target2", entry * 1.10)

        ax1.axhline(y=entry, color="#29B6F6", linestyle="--", linewidth=1.8, label=f"ENTRY: ${entry:.2f}" if "XAUUSD" in signal_data.get("symbol", "") else f"ENTRY: ₹{entry:.2f}")
        ax1.axhline(y=sl, color="#FF1744", linestyle="-.", linewidth=1.8, label=f"STOP LOSS: ${sl:.2f}" if "XAUUSD" in signal_data.get("symbol", "") else f"STOP LOSS: ₹{sl:.2f}")
        ax1.axhline(y=tp1, color="#00E676", linestyle=":", linewidth=1.8, label=f"TARGET 1 (+5%+): ${tp1:.2f}" if "XAUUSD" in signal_data.get("symbol", "") else f"TARGET 1 (+5%+): ₹{tp1:.2f}")
        ax1.axhline(y=tp2, color="#76FF03", linestyle="-", linewidth=2.0, label=f"TARGET 2 (+10%+): ${tp2:.2f}" if "XAUUSD" in signal_data.get("symbol", "") else f"TARGET 2 (+10%+): ₹{tp2:.2f}")

        # Draw Resistance Line if available
        res_level = signal_data.get("resistance_level")
        if res_level:
            ax1.axhline(y=res_level, color="#FFD700", linestyle="-", linewidth=1.5, alpha=0.85, label=f"Breakout Resistance: ₹{res_level:.2f}")

        # Titles and Labels
        symbol = signal_data.get("symbol", "Asset")
        pattern = signal_data.get("pattern_name", "High-Volume Breakout")
        stars = signal_data.get("stars", "⭐️⭐️⭐️⭐️⭐️")
        ax1.set_title(f"{symbol} 1D Daily Breakout Chart | {pattern} {stars}", fontsize=13, fontweight="bold", pad=10, color="#FFFFFF")
        ax1.set_ylabel("Price Level", fontsize=10, color="#B0BEC5")
        ax2.set_ylabel("Volume", fontsize=9, color="#B0BEC5")

        time_labels = [t.strftime("%d %b") if hasattr(t, "strftime") else str(t) for t in df.index]
        step = max(len(df) // 6, 1)
        ax2.set_xticks(indexes[::step])
        ax2.set_xticklabels(time_labels[::step], color="#B0BEC5", rotation=20)

        ax1.grid(True, color="#263238", linestyle=":", alpha=0.6)
        ax2.grid(True, color="#263238", linestyle=":", alpha=0.4)
        ax1.legend(loc="upper left", facecolor="#1E2330", edgecolor="#37474F", fontsize=8.5, labelcolor="#FFFFFF")

        plt.tight_layout()

        out_file = Path(output_path).resolve()
        plt.savefig(out_file, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close()

        return str(out_file)

if __name__ == "__main__":
    from indian_breakout_scanner import IndianBreakoutScanner
    print("Testing ChartGenerator for Indian Stock Breakout Chart...")
    breakouts = IndianBreakoutScanner.scan_all_breakouts()
    b = breakouts[0]
    path = ChartGenerator.generate_signal_chart(b["df"], b, "test_breakout_chart.png")
    print(f"Saved breakout chart PNG to: {path}")
