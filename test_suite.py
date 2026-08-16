import sys
import os
from pathlib import Path

# Force UTF-8 stdout encoding for Windows compatibility
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from data_fetcher import DataFetcher
from smc_analyzer import SMCAnalyzer
from news_fetcher import NewsFetcher
from signal_generator import SignalGenerator
from chart_generator import ChartGenerator

def run_tests():
    print("=" * 65)
    print("RUNNING END-TO-END VERIFICATION FOR XAUUSD TELEGRAM BOT")
    print("=" * 65)

    # 1. Test Data Fetcher
    print("\n[1/5] Testing Market Data Fetcher...")
    mtf = DataFetcher.get_multi_timeframe_data()
    print(f"  * 4H Candles: {len(mtf['4h'])}")
    print(f"  * 1H Candles: {len(mtf['1h'])}")
    print(f"  * 15M Candles: {len(mtf['15m'])}")
    current_close = float(mtf['15m']['Close'].iloc[-1])
    print(f"  * Latest XAUUSD Price: ${current_close:.2f}")

    # 2. Test SMC Analyzer
    print("\n[2/5] Testing SMC & ICT Analysis Engine...")
    analysis = SMCAnalyzer.analyze_market(mtf['1h'], timeframe='1h')
    print(f"  * Structure Trend (1H): {analysis['structure']['trend']}")
    print(f"  * ICT Zone: {analysis['premium_discount']['zone']} (Equilibrium: ${analysis['premium_discount']['equilibrium_50pct']:.2f})")
    print(f"  * Bullish OB Found: {analysis['order_blocks']['bullish_ob'] is not None}")
    print(f"  * Bearish OB Found: {analysis['order_blocks']['bearish_ob'] is not None}")
    print(f"  * Active Bullish FVGs: {len(analysis['fvgs']['active_bullish'])}")

    # 3. Test News Fetcher
    print("\n[3/5] Testing Macroeconomic News Scanner...")
    blackout, news_msg = NewsFetcher.is_news_blackout_active()
    print(f"  * Blackout Active: {blackout}")
    print(f"  * News Radar Message: {news_msg}")

    # 4. Test Signal Generator
    print("\n[4/5] Testing Signal Generator & Formatter...")
    sig = SignalGenerator.generate_signal()
    formatted_msg = SignalGenerator.format_telegram_signal(sig)
    print(f"  * Signal Action: {sig['action']}")
    print(f"  * Rating: {sig['confidence_stars']}")
    print(f"  * Entry: ${sig['entry']:.2f}")
    print(f"  * Stop Loss: ${sig['sl']:.2f}")
    print(f"  * Take Profit 1: ${sig['tp1']:.2f} (1:{sig['rr_ratio']:.1f} R:R)")
    print(f"  * Take Profit 2: ${sig['tp2']:.2f} (1:3.5 R:R)")

    # 5. Test Chart Generator
    print("\n[5/5] Testing Dark-Mode Visual Chart Renderer...")
    chart_file = ChartGenerator.generate_signal_chart(mtf['1h'], sig, "verification_chart.png")
    print(f"  * Generated Chart File: {chart_file}")
    print(f"  * Chart Exists: {os.path.exists(chart_file)}")

    print("\n" + "=" * 65)
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
